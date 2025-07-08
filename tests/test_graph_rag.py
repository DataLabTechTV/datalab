from fixtures import graph_db_schema

from graph.rag import GraphRAG

PROMPTS = (
    "If I like metal artists like Metallica or Iron Maiden, but also listen to IDM, what other artists and genres could I listen to?",
    "What other bands like Anthrax are there?",
)


def test_graph_rag(graph_db_schema):
    gr = GraphRAG(graph_db_schema)

    for prompt in PROMPTS:
        response = gr.invoke(dict(user_query=prompt))
        print(response.content)
