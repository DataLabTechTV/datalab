from typing import Optional

import click

from ml.train import Method


@click.group(help="Machine Learning tasks")
def ml():
    pass


@ml.command(help="Train models")
@click.argument("schema")
@click.option(
    "--text",
    "-t",
    type=click.STRING,
    help="Text column for feature extraction",
)
@click.option("--label", "-l", type=click.STRING, help="Label column")
@click.option(
    "--method",
    "-m",
    type=click.Choice(m.value for m in Method),
    default=Method.LOGREG.value,
    help="Algorithm used for training",
)
def train(schema: str, text: Optional[str], label: Optional[str], method: str):
    pass


@ml.command(help="Test models")
@click.argument("schema")
@click.option(
    "--method",
    "-m",
    type=click.Choice(m.value for m in Method),
    default=Method.LOGREG.value,
    help="Algorithm used for training",
)
def test(schema: str, method: str):
    pass
