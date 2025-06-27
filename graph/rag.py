import re
import textwrap
from enum import Enum

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from langchain_core.language_models.chat_models import BaseChatModel
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
        model: str = "phi4:latest",
        # model: str = "deepseek-r1:7b",
        # model: str = "gemma3:latest",
        column_name: str = "embedding",
    ):
        self.schema = schema
        self.model = model
        self.column_name = column_name

        self.ops = KuzuOps(schema)

        self.chain = self.cypher_prompt | self.llm

    @property
    def cypher_prompt(self) -> ChatPromptTemplate:
        if not hasattr(self, "_cypher_prompt"):
            nodes_schema = self.ops.get_nodes_schema()
            nodes_schema = "\n".join(f"- {node_schema}" for node_schema in nodes_schema)

            rels_schema = self.ops.get_rels_schema()
            rels_schema = "\n".join(f"- {rel_schema}" for rel_schema in rels_schema)

            tpl = textwrap.dedent(
                """
                You are an AI assistant that generates Cypher queries based on user requests and a provided graph schema.

                Input:

                1. Graph schema:
                - Nodes: Each node label with its properties and their types.
                - Relationships: Each relationship type, its direction, and the connected node labels.

                2. User natural language query: a sentence or question describing what data to retrieve.

                Task:

                Step 1: Extract from the user query all relevant entities as nodes and their properties, and the relationships (with directions) between those nodes, but only using the nodes, properties, and relationships defined in the schema.

                Step 2: Write a valid Cypher query that fulfills the user query, strictly using the schema's nodes, properties, and relationships.

                Rules:
                - Only use properties and relationship types defined in the schema.
                - Use exact property names and values as extracted from the user query.
                - If a property value is not specified, do not guess it.
                - Ignore user query requests, and just return the node_id property for nodes matching named entities explicitly mentioned in the user query.
                - Output should be a column with node_id only.
                - Do not make recommendations. This is not a recommendation task.

                ---

                Nodes schema:
                %(nodes_schema)s

                Relationships schema:
                %(rels_schema)s

                User query:
                "{user_query}"

                ---

                Step 1: Extracted entities and relationships:

                [Your output here]

                Step 2: Generated Cypher query:

                [Your output here]
                """
            )

            tpl = tpl.strip("\n")

            tpl %= dict(
                nodes_schema=nodes_schema,
                rels_schema=rels_schema,
            )

            log.debug("cypher prompt:\n{}", tpl)

            self._cypher_prompt = ChatPromptTemplate.from_template(tpl)

        return self._cypher_prompt

    @property
    def llm(self) -> BaseChatModel:
        if not hasattr(self, "_llm"):
            self._llm = ChatOllama(model=self.model, temperature=0)

        return self._llm

    @property
    def context_assembler(self) -> str: ...

    def invoke(self, input, config: RunnableConfig = None):
        return self.chain.invoke(input, config=config)

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
