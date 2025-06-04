import click
from loguru import logger as log

from dlctl.dbt_handler import DBTHandler
from ingest.cli import ingest


@click.group()
def dlctl():
    log.info("Running Data Lab Control")


dlctl.add_command(ingest)


@dlctl.group()
def transform():
    pass


@transform.command()
def all():
    dbt_handler = DBTHandler()
    dbt_handler.run()


if __name__ == "__main__":
    dlctl()
