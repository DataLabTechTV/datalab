from typing import Optional

import click
from loguru import logger as log

from ml.features import Features
from ml.train import Method, train_text_classifier


@click.group(help="Machine Learning tasks")
def ml():
    pass


@ml.command("train", help="Train and test models")
@click.argument("schema")
@click.option(
    "--method",
    "-m",
    type=click.Choice(m.value for m in Method),
    default=Method.LOGREG.value,
    help="Algorithm used for training",
)
@click.option(
    "--features",
    "-f",
    type=click.Choice(f.value for f in Features),
    default=Features.TF_IDF.value,
    help="Features to compute for the training set",
)
@click.option("--k-folds", "-k", type=click.INT, default=5)
def ml_train(schema: str, method: str, features: str, k_folds: int):
    try:
        train_text_classifier(
            schema=schema,
            method=Method(method),
            features=Features(features),
            k_folds=k_folds,
        )
    except Exception as ex:
        log.exception(ex)
