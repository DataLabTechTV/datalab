import click
from loguru import logger as log

from graph.manager import KuzuOps
from shared.lakehouse import Lakehouse
from shared.settings import env


@click.group()
def graph():
    pass


@graph.command(help="Load the graph from a schema inside the marts lakehouse")
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
    log.info("Loading {} into KùzuDB", schema)

    lh = Lakehouse()
    s3_path = lh.export(schema)

    ops = KuzuOps(env.str(f"{schema.upper()}_DB"), overwrite=overwrite)
    ops.load_music_graph(s3_path)


if __name__ == "__main__":
    graph()
