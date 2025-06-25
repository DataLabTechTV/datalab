from enum import Enum

import ollama


class OllamaModel(Enum):
    GEMMA3 = "gemma3:latest"
    NOMIC_EMBED_TEXT = "nomic-embed-text"


class GraphRetriever:
    def __init__(self, prompt: str, model: OllamaModel = OllamaModel.GEMMA3):
        self.prompt = prompt

        if model.value not in ollama.list():
            raise RuntimeError(f"{model.value} not found in ollama server")


class ContextAssembler:
    pass
