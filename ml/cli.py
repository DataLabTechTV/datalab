from datetime import datetime, timedelta

import click
import uvicorn
from loguru import logger as log

from ml.features import Features
from ml.monitor import Monitoring
from ml.server import DEFAULT_HOST, DEFAULT_PORT
from ml.synthetic import simulate_inference
from ml.train import Method, train_text_classifier
from ml.types import InferenceModel

NOW = datetime.now()


@click.group(help="Machine Learning tasks")
def ml():
    pass


@ml.command(
    "train",
    help=(
        "Train and test models using the dataset table under the provided schema from "
        "the stage catalog"
    ),
)
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
@click.option("--k-folds", "-k", type=click.INT, default=3)
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


@ml.command("server", help="Serve the selected models")
@click.option(
    "--host",
    "-h",
    type=click.STRING,
    default=DEFAULT_HOST,
    help="Server host",
)
@click.option("--port", "-p", type=click.INT, default=DEFAULT_PORT, help="Server port")
@click.option("--reload", "-r", is_flag=True, help="Enable reload mode for debugging")
def ml_server(host: str, port: int, reload: bool):
    uvicorn.run(
        "ml.server:app",
        host=host,
        port=port,
        reload=reload,
    )


@ml.command(
    "simulate",
    help=(
        "Simulate inference and feedback requests using the dataset table under the "
        "provided schema from the stage catalog"
    ),
)
@click.argument("schema")
@click.option(
    "--passes",
    "-p",
    type=click.IntRange(min=1),
    default=3,
    help=(
        "Number of passes over the monitor set — this essentially sets the maximum "
        "number of feedback scores per example"
    ),
)
@click.option(
    "--sample-fraction",
    "-s",
    type=click.FloatRange(0, 1, min_open=True),
    help="Sample fraction of the monitor set to provide feedback for",
)
@click.option(
    "--min-feedback-fraction",
    "-mf",
    type=click.FloatRange(0, 1),
    default=0.45,
    help="Minimum fraction of the monitor set to provide feedback for, per pass",
)
@click.option(
    "--max-feedback-fraction",
    "-Mf",
    type=click.FloatRange(0, 1),
    default=0.55,
    help="Maximum fraction of the monitor set to provide feedback for, per pass",
)
@click.option(
    "--min-wrong-fraction",
    "-mw",
    type=click.FloatRange(0, 1),
    default=0.10,
    help="Minimum fraction of wrong feedback, out of the provided feedback",
)
@click.option(
    "--max-wrong-fraction",
    "-Mw",
    type=click.FloatRange(0, 1),
    default=0.25,
    help="Maximum fraction of wrong feedback, out of the provided feedback",
)
@click.option(
    "--min-date",
    "-md",
    type=click.DateTime(),
    default=NOW - timedelta(weeks=4),
    help="Minimum date for simulated requests to occur at",
)
@click.option(
    "--max-date",
    "-Md",
    type=click.DateTime(),
    default=NOW,
    help="Maximum date for simulated requests to occur at",
)
@click.option(
    "--decision-threshold",
    "-t",
    type=click.FloatRange(0, 1, min_open=True, max_open=True),
    default=0.5,
    help="Classification decision threshold (positive = prob >= threshold)",
)
@click.option(
    "--model-uri",
    "-m",
    "model_uris",
    multiple=True,
    required=True,
    help=(
        "Model URI from the MLflow registry in the format models:/<name>/<version> "
        "(e.g., models:/dd_logreg_tfidf/latest)"
    ),
)
@click.option(
    "--batch-size",
    "-b",
    type=click.IntRange(0, min_open=True),
    default=100,
    help="Batch size",
)
def ml_simulate(
    schema: str,
    passes: int,
    sample_fraction: float,
    min_feedback_fraction: float,
    max_feedback_fraction: float,
    min_wrong_fraction: float,
    max_wrong_fraction: float,
    min_date: datetime,
    max_date: datetime,
    decision_threshold: float,
    model_uris: list[str],
    batch_size: int,
):
    inference_models = []

    for model_uri in model_uris:
        _, name, version, *_ = model_uri.split("/")
        inference_model = InferenceModel(name=name, version=version)
        inference_models.append(inference_model)

    simulate_inference(
        schema=schema,
        passes=passes,
        sample_fraction=sample_fraction,
        min_feedback_fraction=min_feedback_fraction,
        max_feedback_fraction=max_feedback_fraction,
        min_wrong_fraction=min_wrong_fraction,
        max_wrong_fraction=max_wrong_fraction,
        min_date=min_date,
        max_date=max_date,
        decision_threshold=decision_threshold,
        inference_models=inference_models,
        batch_size=batch_size,
    )


@ml.group(
    help=(
        "Compute or plot monitoring metrics using the dataset table under the provided "
        "schema from the stage catalog"
    )
)
def monitor():
    pass


@monitor.command(
    "compute",
    help=(
        "Compute monitoring metrics using the dataset table under the provided schema "
        "from the stage catalog"
    ),
)
@click.argument("schema")
@click.option(
    "--model-uri",
    "-m",
    "model_uris",
    multiple=True,
    required=True,
    help=(
        "Model URI from the MLflow registry in the format models:/<name>/<version> "
        "(e.g., models:/dd_logreg_tfidf/latest)"
    ),
)
@click.option(
    "--since",
    "-s",
    type=click.DateTime(),
    help="Inference results start date",
)
@click.option(
    "--until",
    "-u",
    type=click.DateTime(),
    help="Inference results end date",
)
@click.option(
    "--window-size",
    "-w",
    type=click.IntRange(0, min_open=True),
    default=7,
    help="Window size in days",
)
def ml_monitor_compute(
    schema: str,
    model_uris: list[str],
    since: datetime | None,
    until: datetime | None,
    window_size: int,
):
    stats = Monitoring(
        schema,
        model_uris=model_uris,
        since=since,
        until=until,
        window_size=window_size,
    )

    stats.compute()
    stats.store()


@monitor.command(
    "plot",
    help=(
        "Plot monitoring metrics using the dataset table under the provided schema "
        "from the stage catalog"
    ),
)
@click.argument("schema")
@click.option(
    "--model-uri",
    "-m",
    "model_uris",
    multiple=True,
    required=True,
    help=(
        "Model URI from the MLflow registry in the format models:/<name>/<version> "
        "(e.g., models:/dd_logreg_tfidf/latest)"
    ),
)
@click.option(
    "--since",
    "-s",
    type=click.DateTime(),
    help="Inference results start date",
)
@click.option(
    "--until",
    "-u",
    type=click.DateTime(),
    help="Inference results end date",
)
def ml_monitor_plot(
    schema: str,
    model_uris: list[str],
    since: datetime | None,
    until: datetime | None,
):
    stats = Monitoring(
        schema,
        model_uris=model_uris,
        since=since,
        until=until,
    )

    stats.load()
    stats.plot()
