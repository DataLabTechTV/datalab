import re
import textwrap
import threading
import time
from typing import Any, Callable, Optional

import ollama
import pandas as pd
from colorama import Fore
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
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

from graph.ops import KuzuOps

RunnableFn = Callable[[dict[str, Any]], dict[str, Any]]


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


class GraphRetrievalException(Exception):
    def __init__(self, message, query):
        self.query = query
        super().__init__(message)


class ContextAssemblerException(Exception):
    pass


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
    ) -> RunnableFn:
        def run(inputs: dict[str, Any]) -> dict[str, Any]:
            log.info(
                "Querying graph for matching entities (shuffle={}, limit={})",
                shuffle,
                limit,
            )

            query = inputs["query"]
            params = inputs.get("params")

            try:
                context_df = pd.DataFrame(self.graph.query(query, params))

                if shuffle:
                    context_df = context_df.sample(frac=1)

                if limit is not None:
                    context_df = context_df.head(limit)

                return dict(context=context_df)
            except:
                raise GraphRetrievalException("Graph query failed", query=query)

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

    def combined_knn(self, k: int) -> RunnableFn:
        knn_per_node_dfs = []

        def run(inputs: dict[str, Any]) -> dict[str, Any]:
            context = inputs["context"]

            if context is None or len(context) == 0:
                raise ContextAssemblerException("Context not found")

            node_ids = context.node_id.to_list()

            for node_id in node_ids:
                knn_df = self.ops.knn(
                    node_id,
                    max_k=k,
                    max_distance=0.25,
                    exclude=node_ids,
                )

                knn_per_node_dfs.append(knn_df)

            combined_knn_node_ids = (
                pd.concat(knn_per_node_dfs)
                .groupby(["table", "node_id"])
                .mean()
                .reset_index()
                .sort_values("distance")
                .head(k)["node_id"]
                .to_list()
            )

            return dict(knn=combined_knn_node_ids)

        return run

    def nn_sample_shortest_paths(
        self,
        n: int,
        min_length: int,
        max_length: int,
    ) -> RunnableFn:
        def run(inputs: dict[str, Any]) -> dict[str, Any]:
            context = inputs["graph_retrieval"]["context"]

            if context is None or len(context) == 0:
                raise ContextAssemblerException("Context not found")

            source_node_ids = context.node_id.to_list()
            target_node_ids = inputs["combined_knn"]["knn"]

            if target_node_ids is None or len(target_node_ids) == 0:
                raise ContextAssemblerException("Nearest neighbors not found")

            paths_df = self.ops.sample_shortest_paths(
                source_node_ids,
                target_node_ids,
                n,
                min_length,
                max_length,
            )

            return dict(paths=paths_df)

        return run

    def nn_random_walks(
        self,
        n: int,
        min_length: int,
        max_length: int,
    ) -> RunnableFn:
        def run(inputs: dict[str, Any]) -> dict[str, Any]:
            source_node_ids = inputs["combined_knn"]["knn"]

            if source_node_ids is None or len(source_node_ids) == 0:
                raise ContextAssemblerException("Nearest neighbors not found")

            paths_dfs = []

            for source_node_id in source_node_ids:
                paths_df = self.ops.random_walk(
                    source_node_id,
                    n,
                    min_length,
                    max_length,
                )

                paths_dfs.append(paths_df)

            return dict(paths=pd.concat(paths_dfs))

        return run

    def combine_paths(self, inputs: dict[str, Any]) -> dict[str, Any]:
        log.info("Combining paths from multiple outputs")

        dfs = [paths_df["paths"][["paths"]] for paths_df in inputs.values()]
        combined_df = pd.concat(dfs).reset_index(drop=True)

        return dict(paths=combined_df)

    def hydrate_paths(self, inputs: dict[str, Any]) -> dict[str, Any]:
        paths_df = inputs["paths"]

        context_df = self.ops.path_descriptions(
            paths_df,
            exclude_props=[self.column_name],
        )

        return dict(context=context_df)

    @property
    def context_assembler(self) -> Runnable:
        if not hasattr(self, "_context_assembler"):
            self._context_assembler = (
                RunnableParallel(
                    graph_retrieval=RunnablePassthrough(),
                    combined_knn=self.combined_knn(k=10),
                )
                | RunnableParallel(
                    nn_shortest_paths=self.nn_sample_shortest_paths(
                        n=10,
                        min_length=1,
                        max_length=3,
                    ),
                    nn_profile_paths=self.nn_random_walks(
                        n=3,
                        min_length=1,
                        max_length=3,
                    ),
                )
                | self.combine_paths
                | self.hydrate_paths
            )

        return self._context_assembler

    def answer_inputs_transform(self, inputs: dict[str, Any]) -> dict[str, Any]:
        user_query = inputs["user_query"]
        context = inputs["kg"]["context"]
        return dict(user_query=user_query, context=context)

    @property
    def final_prompt(self) -> ChatPromptTemplate:
        if not hasattr(self, "_final_prompt"):
            tpl = textwrap.dedent(
                """
                You are an AI assistant who responds to user queries, taking into account additional context from a knowledge graph, provided in a cypher compatible format.

                Input:
                User query: a question about entities and relationships on a knowledge graph.
                Nodes: relevant nodes to help establish a context.
                Relationships: relevant relationships, between the provided nodes, to help establish a context.

                Task:
                Answer the user based on what you know and the additional knowledge provided by the context.

                User query:
                "{user_query}"

                {context}

                ---

                Here is the answer to your question, based on what I know and the knowledge graph I have access to:

                [Your output here]
                """
            ).strip("\n")

            log.debug("final prompt:\n{}", tpl)

            self._final_prompt = ChatPromptTemplate.from_template(tpl)

        return self._final_prompt

    @property
    def answer_generator(self) -> Runnable:
        if not hasattr(self, "_answer_generator"):
            self._answer_generator = (
                self.answer_inputs_transform | self.final_prompt | self.chat_llm
            )

        return self._answer_generator

    def invoke(self, inputs, config: RunnableConfig = None) -> AIMessage:
        log.info("Running Graph RAG for user query:\n{}", inputs["user_query"])

        self.setup_llm_models()

        chain = (
            RunnableParallel(
                user_query=lambda inputs: inputs["user_query"],
                kg=self.graph_retriever | self.context_assembler,
            )
            | self.answer_generator
        )

        log.debug("user query: {}", inputs["user_query"])
        result = chain.invoke(inputs, config=config)

        return result

    def loader(self, stop_event: threading.Event):
        start_time = time.time()
        symbols = ["⣾", "⣷", "⣯", "⣟", "⡿", "⢿", "⣻", "⣽"]

        while not stop_event.is_set():
            for symbol in symbols:
                elapsed = time.strftime(
                    "%H:%M:%S",
                    time.gmtime(time.time() - start_time),
                )

                print(f"\r⏱ {elapsed} {symbol} ", end="", flush=True)

                time.sleep(0.1)

        print("\b\b\b   ", end="\n\n", flush=True)

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
                        log.remove()

                        stop_event = threading.Event()

                        loader_thread = threading.Thread(
                            target=self.loader,
                            args=(stop_event,),
                        )
                        loader_thread.start()

                        try:
                            response = self.invoke(dict(user_query=user_query))
                            stop_event.set()
                            loader_thread.join()
                            print(response.content)
                        except GraphRetrievalException as e:
                            stop_event.set()
                            loader_thread.join()
                            print(Fore.RED + "Error: " + str(e))
                            print(Fore.MAGENTA + e.query + Fore.RESET)
                        except ContextAssemblerException as e:
                            stop_event.set()
                            loader_thread.join()
                            print(Fore.RED + "Error: " + str(e) + Fore.RESET)
