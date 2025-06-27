import re
import textwrap
from enum import Enum

from langchain.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from platformdirs import user_config_path
from prompt_toolkit import PromptSession
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML, StyleAndTextTuples
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style

from graph.ops import KuzuOps


class OllamaModel(Enum):
    GEMMA3 = "gemma3:latest"
    NOMIC_EMBED_TEXT = "nomic-embed-text"


class GraphRetriever:
    def __init__(
        self,
        schema: str,
        column_name: str,
        model: OllamaModel = OllamaModel.GEMMA3,
    ):
        self.prompt = None

        ops = KuzuOps(schema)
        schema = ops.get_schema()

        cypher_prompt = ChatPromptTemplate.from_template(
            textwrap.dedent(
                """
                You are a graph expert. Given the user's prompt, generate a Cypher query to find matching nodes.

                Graph schema:
                %s
                - Each node may have an `%s` property.

                User prompt:
                "{prompt}"

                Cypher query:
                """
            ).strip("\n")
            % ("\n".join(f"- {rel}" for rel in schema), column_name)
        )

        llm = ChatOllama(model=model.value, temperature=0)
        self.cypher_chain = llm | cypher_prompt

    def retrieve(self):
        cypher = self.cypher_chain.invoke(dict(prompt=self.prompt))
        print(cypher)


class ContextAssembler:
    pass


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


class GraphRAG:
    def __init__(self, schema: str, column_name: str = "embedding"):
        self.gr = GraphRetriever(schema, column_name=column_name)

    def interactive(self):
        config_path = user_config_path("datalab", "DataLabTechTV")
        config_path.mkdir(exist_ok=True)

        history_path = config_path / "graph_rag.history"
        session = PromptSession(history=FileHistory(history_path))

        while True:
            try:
                user_input = session.prompt(
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
                user_input = user_input.strip()

                cmd_info = [f"  {cmd:<10}{info}" for cmd, info in COMMAND_INFO.items()]
                cmd_info = "\n".join(cmd_info)

                match user_input:
                    case ".help":
                        print(f"Available commands:\n{cmd_info}\n")
                    case ".quit":
                        break
                    case ".clear":
                        open(history_path, "w").close()
                        session.default_buffer.history._loaded_strings.clear()
                    case _:
                        self.gr.prompt = user_input
                        self.gr.retrieve()
