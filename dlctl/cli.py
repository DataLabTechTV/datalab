import os
import sys

import click
from loguru import logger as log

import dlctl.tools as T
from dlctl.dbt_handler import DBTHandler
from exports.cli import exports
from graph.cli import graph
from ingest.cli import ingest
from shared.settings import LOCAL_DIR


@click.group(
    invoke_without_command=True,
    help="Data Lab, by https://youtube.com/@DataLabTechTV",
)
@click.option("--debug", is_flag=True, help="Globally enable logging debug mode")
def dlctl(debug: bool):
    log.info("Welcome to Data Lab, by https://youtube.com/@DataLabTechTV")

    log.remove()
    log.add(sys.stderr, level="DEBUG" if debug else "INFO")


dlctl.add_command(ingest)
dlctl.add_command(exports)
dlctl.add_command(graph)


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


@dlctl.group(
    name="docs",
    invoke_without_command=True,
    help="Generate or serve documentation",
)
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
