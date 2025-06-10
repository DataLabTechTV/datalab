import tempfile

import click
import duckdb
from loguru import logger as log

from shared.lakehouse import Lakehouse
from shared.settings import env


@click.group()
def graph():
    pass


@graph.command(help="Load the graph from a schema inside the marts lakehouse")
@click.argument("schema", type=click.STRING)
def load(schema: str):
    log.info("Loading {}", schema)
    lh = Lakehouse()
    lh.export(schema)


if __name__ == "__main__":
    graph()
