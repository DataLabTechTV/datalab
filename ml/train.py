from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

import mlflow
import pandas as pd
from loguru import logger as log
from mlflow.data.dataset import Dataset
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from ml.features import Features, make_text_pipeline
from ml.mlflow import mlflow_end_run, mlflow_start_run
from shared.lakehouse import Lakehouse
from shared.utils import timed

Folds = list[tuple[list[int], list[int]]]


class Method(Enum):
    XGBOOST = "xgboost"
    LOGREG = "logreg"


@dataclass
class MLDataset:
    train: pd.DataFrame
    test: pd.DataFrame
    folds: Folds
    mlflow_train: Dataset
    mlflow_test: Dataset
    mlflow_tags: dict[str, Any]


def make_logreg() -> tuple[Pipeline, dict[str, Any]]:
    pipe = Pipeline(
        [
            ("logreg", LogisticRegression(max_iter=500, solver="liblinear")),
        ]
    )

    param_grid = {
        "logreg__C": [0.01, 0.1, 1, 10],
        "logreg__penalty": ["l1", "l2"],
    }

    return pipe, param_grid


def make_xgboost() -> tuple[Pipeline, dict[str, Any]]:
    pipe = Pipeline(
        [
            ("xgboost", XGBClassifier()),
        ]
    )

    param_grid = {
        "xgboost__max_depth": [3, 6],
        "xgboost__learning_rate": [0.05, 0.1],
        "xgboost__n_estimators": [100, 200],
        "xgboost__subsample": [0.8, 1.0],
    }

    return pipe, param_grid


def load_dataset(schema: str, k_folds: Literal[3, 5, 10]) -> MLDataset:
    lh = Lakehouse(read_only=True)

    train = lh.load_docs_train_set("stage", schema, "dataset", k_folds=k_folds)
    test = lh.load_docs_test_set("stage", schema, "dataset")
    snapshot_id = lh.snapshot_id("stage")

    folds = []

    for _, fold in train.groupby("fold_id"):
        test_idx = fold.index.to_list()
        train_idx = list(set(train.index) - set(fold.index))
        folds.append((train_idx, test_idx))

    train_dataset = mlflow.data.from_pandas(
        train,
        targets="label",
        name="train",
    )

    test_dataset = mlflow.data.from_pandas(
        test,
        targets="label",
        name="test",
    )

    return MLDataset(
        train=train,
        test=test,
        folds=folds,
        mlflow_train=train_dataset,
        mlflow_test=test_dataset,
        mlflow_tags={
            "lakehouse.catalog": "stage",
            "lakehouse.schema": schema,
            "lakehouse.table_name": "dataset",
            "lakehouse.snapshot_id": str(snapshot_id),
            "lakehouse.train.k_folds": str(k_folds),
        },
    )


@timed
def train_text_classifier(
    schema: str,
    method: Method,
    features: Features,
    k_folds: Literal[3, 5, 10] = 3,
    scoring: str = "f1",
):
    ds = load_dataset(schema, k_folds)

    features_pipe = make_text_pipeline(features)

    match method:
        case Method.LOGREG:
            classifier_pipe, param_grid = make_logreg()
        case Method.XGBOOST:
            classifier_pipe, param_grid = make_xgboost()
        case _:
            raise ValueError(f"Method unsupported: {method}")

    pipe = Pipeline(features_pipe.steps + classifier_pipe.steps)

    mlflow_start_run(
        experiment_name=schema,
        run_name=f"{method.value}_{features.value}",
        tags=dict(
            method=method.value,
            features=features.value,
            k_folds=k_folds,
            scoring=scoring,
            param_grid=param_grid,
        ),
        datasets=[ds.mlflow_train, ds.mlflow_test],
        dataset_tags=ds.mlflow_tags,
    )

    log.info(
        "Training model using {} and {} with {}-fold CV, optimizing {} "
        "hyperparameters: {}",
        features,
        method,
        k_folds,
        len(param_grid),
        ", ".join(p.split("__")[-1] for p in param_grid.keys()),
    )

    search = GridSearchCV(
        estimator=pipe,
        param_grid=param_grid,
        cv=ds.folds,
        scoring=scoring,
        n_jobs=1,
        verbose=3,
    )

    search.fit(ds.train.text.to_list(), ds.train.label)

    log.info("Best params: {}", search.best_params_)
    log.info("Best F1 score: {}", search.best_score_)

    log.info("Evaluating model on the test set")

    y_pred = search.predict(ds.test.text)

    acc = accuracy_score(ds.test.label, y_pred)
    f1 = f1_score(ds.test.label, y_pred)

    log.info("Accuracy: {}", acc)
    log.info("F1 score: {}", f1)

    mlflow_end_run(
        model_name=f"{schema}_{method.value}_{features.value}",
        model=search.best_estimator_,
        params=search.best_params_,
        metrics={
            scoring: search.best_score_,
            "test_accuracy": acc,
            "test_f1": f1,
        },
        train=ds.train,
    )
