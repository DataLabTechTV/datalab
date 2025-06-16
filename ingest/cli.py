import click
from loguru import logger as log

from ingest.handler import handle_hugging_face, handle_kaggle, handle_standalone
from shared.storage import Storage, StoragePrefix


@click.group(help="Manage dataset ingestion")
def ingest():
    pass


@ingest.command(help="Handle ingestion into a dated directory structure")
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


@ingest.command(help="List ingested datasets")
@click.option(
    "--all",
    "-a",
    "include_all",
    is_flag=True,
    help="List all directories, not just the latest",
)
def ls(include_all: bool):
    versions = "all" if include_all else "latest"
    log.info("Listing ingested datasets: {} versions", versions)

    storage = Storage(prefix=StoragePrefix.INGEST)
    storage.ls(include_all=include_all)


@ingest.command(help="Delete old dataset ingestions, only keeping the latest datasets")
def prune():
    log.info("Pruning ingested datasets")
    storage = Storage(prefix=StoragePrefix.INGEST)
    storage.prune()


if __name__ == "__main__":
    ingest()
