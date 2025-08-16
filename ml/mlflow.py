import tomllib
from typing import Any

import mlflow
import mlflow.sklearn
import pandas as pd
from loguru import logger as log
from mlflow.data.dataset import Dataset
from mlflow.models import infer_signature
from sklearn.pipeline import Pipeline

from shared.settings import env


def mlflow_start_run(
    experiment_name: str,
    run_name: str,
    tags: dict[str, Any],
    datasets: list[Dataset],
    dataset_tags: dict[str, Any],
):
    tracking_uri = env.str("MLFLOW_TRACKING_URI")
    mlflow.set_tracking_uri(tracking_uri)
    log.info("MLflow tracking URI: {}", tracking_uri)

    mlflow.set_experiment(experiment_name)
    log.info("MLflow experiment: {}", experiment_name)

    mlflow.start_run(run_name=run_name)
    log.info("MLflow run: {}", run_name)

    log.info("MLflow: logging tags and input datasets")

    mlflow.set_tags(tags | dataset_tags)

    contexts = [ds.name for ds in datasets]
    tags_list = [dataset_tags for _ in datasets]
    mlflow.log_inputs(datasets=datasets, contexts=contexts, tags_list=tags_list)


def mlflow_end_run(
    model_name: str,
    model: Pipeline,
    params: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    train: pd.DataFrame | None = None,
):
    signature = None

    if train is not None:
        log.info("MLflow: inferring model signature")
        model_input = train.drop(columns=["label", "fold_id"])
        model_output = model.predict(model_input)
        signature = infer_signature(model_input, model_output)

    log.info("Extracting pip requirements from uv")
    pyproject = tomllib.load(open("pyproject.toml", "rb"))
    requirements = pyproject.get("project", {}).get("dependencies", {})

    log.info("MLflow: logging model")

    mlflow.sklearn.log_model(
        sk_model=model,
        name=model_name,
        registered_model_name=model_name,
        signature=signature,
        pip_requirements=requirements,
    )

    if params is not None:
        log.info("MLflow: logging parameters")
        mlflow.log_params(params)

    if metrics is not None:
        log.info("MLflow: logging metrics")
        mlflow.log_metrics(metrics)

    mlflow.end_run()
