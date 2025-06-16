import os
import sys

import click
from loguru import logger as log

import shared.tools as T
from dlctl.dbt_handler import DBTHandler
from export.cli import export
from graph.cli import graph
from ingest.cli import ingest
from shared.lakehouse import Lakehouse
from shared.settings import LOCAL_DIR, MART_DB_VARS, env
from shared.storage import Storage, StoragePrefix


@click.group(help="Data Lab, by https://youtube.com/@DataLabTechTV")
@click.option("--debug", is_flag=True, help="Globally enable logging debug mode")
def dlctl(debug: bool):
    log.info("Welcome to Data Lab, by https://youtube.com/@DataLabTechTV")

    log.remove()
    log.add(sys.stderr, level="DEBUG" if debug else "INFO")


# External
# ========

dlctl.add_command(ingest)
dlctl.add_command(export)
dlctl.add_command(graph)

# Backups
# =======


@dlctl.group(help="Manage catalog backups")
def backup():
    pass


@backup.command(name="create", help="Backup catalog into object storage")
def backup_create():
    log.info("Creating a catalog backup")

    source_files = [env.str("ENGINE_DB"), env.str("STAGE_DB")]
    source_files += (env.str(varname) for varname in MART_DB_VARS)

    for source_file in source_files:
        source_path = os.path.join(LOCAL_DIR, source_file)

        if not os.path.exists(source_path):
            log.error("source path doesn't exist: {}", source_path)
            return

    s = Storage(prefix=StoragePrefix.BACKUPS)
    s3_backup_path = s.get_dir("catalog", dated=True)
    s.upload_files(LOCAL_DIR, source_files, s3_backup_path)
    s.upload_manifest("catalog", latest=s3_backup_path)

    log.info("Catalog backup created: {}", s3_backup_path)


@backup.command(help="Restore catalog into directory")
@click.option("--target", default=LOCAL_DIR, type=click.STRING, help="Target directory")
def restore(target: str):
    log.info("Restoring catalog backup to {}", target)

    os.makedirs(target, exist_ok=True)

    s = Storage(prefix=StoragePrefix.BACKUPS)
    manifest = s.load_manifest("catalog")

    if manifest is None or "latest" not in manifest:
        log.error("No catalog backups found in manifest")
        return

    s.download_dir(manifest["latest"], target)


@backup.command(help="List catalog backups")
def ls():
    log.info("Listing all catalog backups")

    storage = Storage(prefix=StoragePrefix.BACKUPS)
    storage.ls(include_all=True)


# Transform
# =========


@dlctl.command(help="Transform datasets (ETL via dbt and DuckDB/DuckLake)")
@click.option(
    "--model",
    "-m",
    "models",
    multiple=True,
    type=click.STRING,
    help="Model name to transform (can be used multiple times)",
)
@click.option("--debug", is_flag=True, help="Run dbt with the debug flag")
def transform(models: tuple[str], debug: bool):
    dbt_handler = DBTHandler(debug=debug)
    dbt_handler.run(models)


# Test
# ====


@dlctl.command(name="test", help="Run data tests")
def test():
    dbt_handler = DBTHandler()
    dbt_handler.test()


# Documentation
# =============


@dlctl.group(name="docs", help="Generate or serve documentation")
def docs():
    pass


@docs.command(name="generate", help="Generate documentation (see transform/target)")
def docs_generate():
    dbt_handler = DBTHandler()
    dbt_handler.docs_generate()


@docs.command(name="serve", help="Serve documentation (port 8080)")
def docs_serve():
    dbt_handler = DBTHandler()
    dbt_handler.docs_serve()


# Tools
# =====


@dlctl.group(help="Standalone tools for ops and other tasks")
def tools():
    pass


@tools.command(
    help="Generate scripts/init.sql to be used with duckdb -init",
)
@click.option(
    "--path",
    type=click.STRING,
    default=os.path.join(LOCAL_DIR, "init.sql"),
    help="Custom output path for the init.sql file",
)
def generate_init_sql(path: str):
    T.generate_init_sql(path)


if __name__ == "__main__":
    dlctl()
