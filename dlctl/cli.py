import sys

import click
from loguru import logger as log

from dlctl.dbt_handler import DBTHandler
from exports.cli import exports
from graph.cli import graph
from ingest.cli import ingest


@click.group()
@click.option("--debug", is_flag=True, help="Globally enable logging debug mode")
def dlctl(debug: bool):
    log.info("Welcome to Data Lab, by https://youtube.com/@DataLabTechTV")

    log.remove()
    log.add(sys.stderr, level="DEBUG" if debug else "INFO")


dlctl.add_command(ingest)
dlctl.add_command(exports)
dlctl.add_command(graph)


@dlctl.command()
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


@dlctl.command(name="test")
def test():
    dbt_handler = DBTHandler()
    dbt_handler.test()


@dlctl.group(name="docs")
def docs():
    pass


@docs.command(name="generate")
def docs_generate():
    dbt_handler = DBTHandler()
    dbt_handler.docs_generate()


@docs.command(name="serve")
def docs_serve():
    dbt_handler = DBTHandler()
    dbt_handler.docs_serve()


if __name__ == "__main__":
    dlctl()
