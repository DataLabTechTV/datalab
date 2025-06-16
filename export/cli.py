import click
from loguru import logger as log

from shared.lakehouse import Lakehouse
from shared.settings import MART_SCHEMAS
from shared.storage import Storage, StoragePrefix


@click.group(help="Manage dataset exporting")
def export():
    pass


@export.command(help="Export latest version of dataset from data mart")
@click.argument("catalog", type=click.Choice(MART_SCHEMAS))
@click.argument("schema")
def dataset(catalog: str, schema: str):
    lh = Lakehouse()
    lh.export(catalog, schema)


@export.command(help="List exported datasets")
@click.option(
    "--all",
    "-a",
    "include_all",
    is_flag=True,
    help="List all directories, not just the latest",
)
def ls(include_all: bool):
    versions = "all" if include_all else "latest"
    log.info("Listing exported datasets: {} versions", versions)

    storage = Storage()
    storage.ls(StoragePrefix.EXPORTS, include_all=include_all)


@export.command(help="Delete old dataset exports, only keeping the latest datasets")
def prune():
    log.info("Pruning exported datasets")
    storage = Storage()
    storage.prune(StoragePrefix.EXPORTS)


if __name__ == "__main__":
    export()
