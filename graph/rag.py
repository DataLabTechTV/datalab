import re
import textwrap
from typing import Any, Callable, Optional

import ollama
import pandas as pd
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_kuzu.chains.graph_qa.kuzu import extract_cypher, remove_prefix
from langchain_kuzu.chains.graph_qa.prompts import KUZU_GENERATION_PROMPT
from langchain_kuzu.graphs.kuzu_graph import KuzuGraph
from langchain_ollama import ChatOllama
from loguru import logger as log
from platformdirs import user_config_path
from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML, StyleAndTextTuples
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style

from graph.ops import KuzuOps, KuzuTableType

COMMAND_INFO = {
    ".help": "Shows this message",
    ".quit": "Exits to the command line",
    ".clear": "Clear history file",
}


class CommandLexer(Lexer):
    COMMANDS = re.compile(rf"({'|'.join(COMMAND_INFO.keys())})\b(.*)")

    def lex_document(self, document: Document) -> callable:
        text = document.text

        def get_line(lineno):
            tokens: StyleAndTextTuples = []
            cmd_match = self.COMMANDS.match(text)
            if cmd_match:
                tokens.append(("class:cmd", cmd_match.group(1)))
                tokens.append(("", cmd_match.group(2)))
            else:
                tokens.append(("", text))
            return tokens

        return get_line


class GraphRAG(Runnable):
    def __init__(
        self,
        schema: str,
        code_model: str = "phi4:latest",
        chat_model: str = "gemma3:latest",
        column_name: str = "embedding",
    ):
        self.schema = schema
        self.code_model = code_model
        self.chat_model = chat_model
        self.column_name = column_name

        self.ops = KuzuOps(schema)

        self.graph = KuzuGraph(
            self.ops.conn.database,
            allow_dangerous_requests=True,
        )

    def setup_llm_models(self):
        ollama_models = {m.model for m in ollama.list().models}

        for model in self.code_model, self.chat_model:
            if model not in ollama_models:
                log.warning("{}: ollama model not found, pulling...", model)
                ollama.pull(model)

    @property
    def code_llm(self) -> BaseChatModel:
        if not hasattr(self, "_code_llm"):
            self._chat_llm = ChatOllama(model=self.code_model, temperature=0.0)

        return self._chat_llm

    @property
    def chat_llm(self) -> BaseChatModel:
        if not hasattr(self, "_chat_llm"):
            self._chat_llm = ChatOllama(model=self.chat_model, temperature=0.2)

        return self._chat_llm

    @property
    def entities_prompt(self) -> ChatPromptTemplate:
        if not hasattr(self, "_entities_prompt"):
            tpl = textwrap.dedent(
                """
                You are an AI assistant that extracts entities from a given user query using named entity recognition and matches them to nodes in a knowledge graph, returning the node_id properties of those nodes, and nothing more.

                Input:
                User query: a sentence or question mentioning entities to retrieve from the knowledge graph.

                Task:
                Extract all relevant entities from the user query as nodes represented by their node_id property.

                Rules:
                - Only use node properties defined in the schema.
                - Use exact property names and values as extracted from the user query.
                - If a property value is not specified, do not guess it.
                - Ignore user query requests, and just return the node_id property for nodes matching named entities explicitly mentioned in the user query.
                - Do not make recommendations. Only return the node_id properties for extracted entities that have a node in the graph.

                Example:

                If the user mentions Nirvana and there is an artist property on a Track node, then all nodes matching Nirvana should be retrieved as follows:

                ```cypher
                MATCH (t:Track)
                WHERE LOWER(t.artist) = LOWER("Nirvana")
                RETURN t.node_id AS node_id;
                ```

                If, in addition to Nirvana, the user algo mentions the grunge genre, and there is a genre property of a Genre node, then all nodes matching grunge should be added to be previous query as follows:

                ```cypher
                MATCH (t:Track)
                WHERE LOWER(t.artist) = LOWER("Nirvana")
                RETURN t.node_id AS node_id

                UNION

                MATCH (g:Genre)
                WHERE LOWER(g.genre) = LOWER("grunge")
                RETURN g.node_id AS node_id
                ```

                User query:
                "{user_query}"

                ---

                Here are the node_id properties for all nodes matching the extracted entities:

                [Your output here]
                """
            ).strip("\n")

            log.debug("entities prompt:\n{}", tpl)

            self._entities_prompt = ChatPromptTemplate.from_template(tpl)

        return self._entities_prompt

    def cypher_from_ai_message(self, message: AIMessage) -> dict[str, Any]:
        cypher = remove_prefix(extract_cypher(message.content), "cypher")
        log.debug("cypher from ai message:\n{}", cypher)
        return dict(query=cypher)

    def query_graph(
        self,
        shuffle: bool = False,
        limit: Optional[int] = None,
    ) -> Callable[[dict[str, Any]], dict[str, Any]]:
        def run(inputs: dict[str, Any]) -> dict[str, Any]:
            query = inputs["query"]
            params = inputs.get("params")

            context_df = pd.DataFrame(self.graph.query(query, params))

            if shuffle:
                context_df = context_df.sample(frac=1)

            if limit is not None:
                context_df = context_df.head(limit)

            return dict(context=context_df)

        return run

    @property
    def graph_retriever(self) -> Runnable:
        if not hasattr(self, "_graph_retriever"):

            def entities_prompt_to_kuzu_inputs(
                inputs: dict[str, Any],
            ) -> dict[str, str]:
                self.graph.refresh_schema()

                return {
                    "schema": self.graph.get_schema,
                    "question": self.entities_prompt.format(**inputs),
                }

            self._graph_retriever = (
                entities_prompt_to_kuzu_inputs
                | KUZU_GENERATION_PROMPT
                | self.code_llm
                | self.cypher_from_ai_message
                | self.query_graph(shuffle=True, limit=100)
            )

        return self._graph_retriever

    def combined_knn(self, k: int) -> Callable[[dict[str, Any]], dict[str, Any]]:
        knn_per_node_dfs = []

        def run(inputs: dict[str, Any]) -> dict[str, Any]:
            context = inputs["context"]

            for node_id in context.node_id:
                knn_df = self.ops.knn(node_id, k=k)
                knn_per_node_dfs.append(knn_df)

            combined_knn_node_ids = (
                pd.concat(knn_per_node_dfs)
                .groupby("node_id")
                .mean()
                .reset_index()
                .sort_values("distance")
                .head(k)["node_id"]
                .to_list()
            )

            return dict(knn=combined_knn_node_ids)

        return run

    @property
    def context_assembler(self) -> Runnable:
        if not hasattr(self, "_context_assembler"):
            self._context_assembler = self.combined_knn(k=100)

        return self._context_assembler

    def invoke(self, inputs, config: RunnableConfig = None) -> dict[str, Any]:
        self.setup_llm_models()

        chain = self.graph_retriever | self.context_assembler

        log.debug("user query: {}", inputs["user_query"])
        result = chain.invoke(inputs, config=config)

        return result

    def interactive(self):
        config_path = user_config_path("datalab", "DataLabTechTV")
        config_path.mkdir(exist_ok=True)

        history_path = config_path / "graph_rag.history"
        session = PromptSession(history=FileHistory(history_path))

        while True:
            try:
                user_query = session.prompt(
                    ">>> ",
                    lexer=CommandLexer(),
                    placeholder=HTML("<faded>Enter a prompt (or .help)</faded>"),
                    style=Style.from_dict(
                        {
                            "faded": "fg:#8a8a8a",
                            "cmd": "fg:#00aeff",
                        }
                    ),
                )
            except (KeyboardInterrupt, EOFError):
                break
            else:
                user_query = user_query.strip()

                cmd_info = [f"  {cmd:<10}{info}" for cmd, info in COMMAND_INFO.items()]
                cmd_info = "\n".join(cmd_info)

                match user_query:
                    case ".help":
                        print(f"Available commands:\n{cmd_info}\n")
                    case ".quit":
                        break
                    case ".clear":
                        open(history_path, "w").close()
                        session.default_buffer.history._loaded_strings.clear()
                    case _:
                        print(self.invoke(user_query=user_query))
