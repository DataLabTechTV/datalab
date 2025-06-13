import os

import click
from loguru import logger as log

from graph.embedding import NodeEmbedding, NodeEmbeddingAlgo
from graph.ops import KuzuOps
from shared.lakehouse import Lakehouse
from shared.settings import env


@click.group()
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
@click.option(
    "--force-export",
    is_flag=True,
    help="Force export from graphs data mart, even if an export already exists",
)
def load(schema: str, overwrite: bool, force_export: bool):
    graph_catalog = os.path.splitext(os.path.split(env.str("GRAPHS_MART_DB"))[-1])[0]

    log.info("Loading {}.{} into KùzuDB", graph_catalog, schema)

    lh = Lakehouse()

    if force_export:
        s3_path = lh.export(graph_catalog, schema)
    else:
        s3_path = lh.latest_export(graph_catalog, schema)

        if s3_path is None:
            log.warning("Export not found, exporting {}.{}...", graph_catalog, schema)
            s3_path = lh.export(graph_catalog, schema)
        else:
            log.info("Latest export found at {}", s3_path)

    try:
        ops = KuzuOps(schema, overwrite=overwrite)
        ops.load_music_graph(s3_path)
    except Exception as e:
        log.error(e)


@graph.group()
def compute():
    pass


@compute.command(help="Compute node embeddings using the selected algorithm")
@click.argument("schema", type=click.STRING)
@click.option(
    "--batch-size",
    "-bs",
    default=512,
    type=click.INT,
    help="Batch size corresponding to the number of nodes for which to load neighbors",
)
@click.option(
    "--algo",
    "-a",
    type=click.Choice(algo.name for algo in NodeEmbeddingAlgo),
    default=NodeEmbeddingAlgo.FRP.name,
    help="Node embedding algorithm",
)
def embeddings(schema: str, batch_size: int, algo: str):
    try:
        e = NodeEmbedding(schema, batch_size=batch_size, algo=NodeEmbeddingAlgo[algo])
        e.train()
    except Exception as e:
        log.error(e)


if __name__ == "__main__":
    graph()
