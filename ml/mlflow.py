from typing import Any

import mlflow
from loguru import logger as log
from mlflow.data.dataset import Dataset

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

    mlflow.set_tags(tags | dataset_tags)

    contexts = [ds.name for ds in datasets]
    tags_list = [dataset_tags for _ in datasets]
    mlflow.log_inputs(datasets=datasets, contexts=contexts, tags_list=tags_list)


def mlflow_end_run(params: dict[str, Any], metrics: dict[str, Any]):
    mlflow.log_params(params)
    mlflow.log_metrics(metrics)
    mlflow.end_run()
