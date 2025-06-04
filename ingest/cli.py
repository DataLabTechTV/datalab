import click
from loguru import logger as log

from ingest.handler import handle_hugging_face, handle_kaggle, handle_standalone


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
    elif dataset.startswith("https://www.kaggle.com/datasets/"):
        handle_kaggle(dataset_url=dataset)
    elif dataset.startswith("https://huggingface.co/datasets/"):
        handle_hugging_face(dataset_url=dataset)


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
