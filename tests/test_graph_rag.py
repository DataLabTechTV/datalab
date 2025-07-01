from pathlib import Path

import pytest

from graph.rag import GraphRAG
from shared.settings import LOCAL_DIR, env

PROMPTS = (
    "If I like metal artists like Metallica or Iron Maiden, but also listen to IDM, what other artists and genres could I listen to?",
)


def setup_module():
    db_path = Path(LOCAL_DIR) / env.str("MUSIC_TASTE_GRAPH_DB")

    if not db_path.exists():
        pytest.skip(f"Database not found at {db_path}, skipping test.")


def test_graph_rag():
    gr = GraphRAG("music_taste")

    for prompt in PROMPTS:
        response = gr.invoke(dict(user_query=prompt))
        print(response)
