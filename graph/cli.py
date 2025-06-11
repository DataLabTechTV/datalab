import os

import click
from loguru import logger as log

from graph.manager import KuzuOps
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
    "--latest-export",
    is_flag=True,
    help="Use the latest export, if one exists",
)
def load(schema: str, overwrite: bool, latest_export: bool):
    graph_catalog = os.path.splitext(os.path.split(env.str("GRAPHS_MART_DB"))[-1])[0]

    log.info("Loading {}.{} into KùzuDB", graph_catalog, schema)

    lh = Lakehouse()

    if latest_export:
        s3_path = lh.latest_export(graph_catalog, schema)

        if s3_path is not None:
            log.info("Reusing latest export found at {}", s3_path)

    if not latest_export or s3_path is None:
        s3_path = lh.export(graph_catalog, schema)

    ops = KuzuOps(env.str(f"{schema.upper()}_GRAPH_DB"), overwrite=overwrite)
    ops.load_music_graph(s3_path)


if __name__ == "__main__":
    graph()
