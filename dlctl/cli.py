import click
from loguru import logger as log

from ingest.cli import ingest


@click.group()
def dlctl():
    log.info("Running Data Lab Control")


dlctl.add_command(ingest)

if __name__ == "__main__":
    dlctl()
