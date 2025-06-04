import click
from loguru import logger as log

from ingest.handler import handle_standalone


@click.group()
def ingest():
    pass


@ingest.command()
@click.argument("dataset", type=click.STRING)
@click.option(
    "-m",
    "--manual",
    is_flag=True,
    help="Dataset argument will be used to create an empty directory in S3",
)
def dataset(dataset: str, manual: bool):
    log.info("Running ingestion for: {}", dataset)

    if manual:
        handle_standalone(dataset)


@ingest.command()
@click.option(
    "-a",
    "include_all",
    is_flag=True,
    help="List all directories, not just the latest",
)
def ls(include_all: bool):
    if include_all:
        log.info("Listing all datasets")
    else:
        log.info("Listing latest datasets")


if __name__ == "__main__":
    ingest()
