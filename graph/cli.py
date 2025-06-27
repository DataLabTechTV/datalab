import os

import click
from loguru import logger as log

from graph.embedding import NodeEmbedding, NodeEmbeddingAlgo
from graph.ops import KuzuOps
from graph.rag import GraphRAG
from shared.lakehouse import Lakehouse
from shared.settings import env


@click.group(help="Load, manage, and run graph computations on top of KùzuDB")
def graph():
    pass


@graph.command(help="Load the graph from a schema within the provided catalog")
@click.argument("schema", type=click.STRING)
@click.option(
    "--overwrite",
    is_flag=True,
    help=(
        "If the database path set in the environment variable <SCHEMA>_DB exists, it "
        "will be overwritten"
    ),
)
def load(schema: str, overwrite: bool):
    graph_catalog = os.path.splitext(os.path.split(env.str("GRAPHS_MART_DB"))[-1])[0]

    log.info("Loading {}.{} into KùzuDB", graph_catalog, schema)

    lh = Lakehouse()

    s3_path = lh.latest_export(graph_catalog, schema)

    if s3_path is None:
        log.error("Export not found, exporting {}.{}...", graph_catalog, schema)
        return

    log.info("Latest export found at {}", s3_path)

    try:
        ops = KuzuOps(schema, overwrite=overwrite)
        ops.load_music_graph(s3_path)
    except Exception as e:
        log.error(e)


@graph.group(help="Run a graph computation workflow")
def compute():
    pass


@compute.command(help="Compute node embeddings using the selected algorithm")
@click.argument("schema", type=click.STRING)
@click.option(
    "--dimension",
    "-d",
    default=128,
    type=click.INT,
    help="Dimension of the embeddings",
)
@click.option(
    "--batch-size",
    "-b",
    default=512,
    type=click.INT,
    help="Batch size corresponding to the number of nodes for which to load neighbors",
)
@click.option(
    "--epochs",
    "-e",
    default=1,
    type=click.INT,
    help="Number of epochs (i.e., global passes)",
)
@click.option(
    "--algo",
    "-a",
    type=click.Choice(algo.name for algo in NodeEmbeddingAlgo),
    default=NodeEmbeddingAlgo.FRP.name,
    help="Node embedding algorithm",
)
def embeddings(schema: str, dimension: int, batch_size: int, epochs: int, algo: str):
    try:
        e = NodeEmbedding(
            schema,
            dim=dimension,
            batch_size=batch_size,
            epochs=epochs,
            algo=NodeEmbeddingAlgo[algo],
        )
        e.train()
    except Exception as e:
        log.exception(e)


@graph.command()
@click.argument("schema", type=click.STRING)
def reindex(schema: str):
    try:
        ops = KuzuOps(schema)
        ops.reindex_embeddings()
    except Exception as e:
        log.error(e)


@graph.command()
@click.argument("schema", type=click.STRING)
def rag(schema: str):
    gr = GraphRAG(schema)
    gr.interactive()


if __name__ == "__main__":
    graph()
