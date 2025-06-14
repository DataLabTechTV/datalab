import click
from loguru import logger as log

from shared.storage import Storage, StoragePrefix


@click.group(invoke_without_command=True, help="Manage exported datasets")
def exports():
    pass


@exports.command(help="List exported datasets")
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


@exports.command(help="Delete old dataset exports, only keeping the latest datasets")
def prune():
    log.info("Pruning exported datasets")
    storage = Storage()
    storage.prune(StoragePrefix.EXPORTS)


if __name__ == "__main__":
    exports()
