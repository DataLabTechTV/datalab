import click
from loguru import logger as log

from dlctl.dbt_handler import DBTHandler
from ingest.cli import ingest


@click.group()
def dlctl():
    log.info("Running Data Lab Control")


dlctl.add_command(ingest)


@dlctl.command()
@click.option(
    "--model",
    "-m",
    "models",
    multiple=True,
    type=click.STRING,
    help="Model name to transform (can be used multiple times)",
)
def transform(models: tuple[str]):
    dbt_handler = DBTHandler()
    dbt_handler.run(models)


if __name__ == "__main__":
    dlctl()
