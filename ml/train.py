from enum import Enum
from typing import Any, Literal, Optional

import mlflow
from loguru import logger as log
from mlflow.data.dataset_source import DatasetSource
from mlflow.data.pandas_dataset import PandasDataset
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from ml.features import Features, make_text_pipeline
from shared.lakehouse import Lakehouse
from shared.settings import env
from shared.utils import timed

Folds = list[tuple[list[int], list[int]]]


class Method(Enum):
    XGBOOST = "xgboost"
    LOGREG = "logreg"


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


class DuckLakeTableDatasetSource(DatasetSource):
    def __init__(
        self,
        catalog: str,
        schema: str,
        table_name: str,
        snapshot_id: str,
        where: Optional[str],
        k_folds: Optional[str] = None,
    ):
        self.catalog = catalog
        self.schema = schema
        self.table_name = table_name
        self.snapshot_id = snapshot_id
        self.where = where
        self.k_folds = k_folds

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in vars(self)}

    @classmethod
    def from_dict(cls, source_dict):
        return cls(**source_dict)

    def __repr__(self):
        attrs = ", ".join(f"{k}='{v}'" for k, v in vars(self).items())
        return f"DuckLakeTableDatasetSource({attrs})"


def load_dataset(
    schema: str,
    k_folds: Literal[3, 5, 10],
) -> tuple[PandasDataset, PandasDataset, Folds]:
    lh = Lakehouse()

    train = lh.load_docs_train_set("stage", schema, "dataset", k_folds=k_folds)
    test = lh.load_docs_test_set("stage", schema, "dataset")
    snapshot_id = lh.snapshot_id("stage")

    folds = []

    for _, fold in train.groupby("fold_id"):
        test_idx = fold.index.to_list()
        train_idx = list(set(train.index) - set(fold.index))
        folds.append((train_idx, test_idx))

    train_dataset = mlflow.data.from_pandas(
        df=train,
        source=DuckLakeTableDatasetSource(
            catalog="stage",
            schema=schema,
            table_name="dataset",
            snapshot_id=snapshot_id,
            where="NOT is_test",
            k_folds=k_folds,
        ),
        targets="label",
        name="train",
    )

    test_dataset = mlflow.data.from_pandas(
        df=test,
        source=DuckLakeTableDatasetSource(
            catalog="stage",
            schema=schema,
            table_name="dataset",
            snapshot_id=snapshot_id,
            where="is_test",
        ),
        targets="label",
        name="test",
    )

    return train_dataset, test_dataset, folds


@timed
def train_text_classifier(
    schema: str,
    method: Method,
    features: Features,
    k_folds: Literal[3, 5, 10] = 3,
    scoring: str = "f1",
):
    tracking_uri = env.str("MLFLOW_TRACKING_URI")
    mlflow.set_tracking_uri(tracking_uri)
    log.info("MLflow tracking URI: {}", tracking_uri)

    mlflow.set_experiment(schema)
    log.info("MLflow experiment: {}", schema)

    run_name = f"{method.value}_{features.value}"
    mlflow.start_run(run_name=run_name)

    mlflow.set_tag("method", method.value)
    mlflow.set_tag("features", features.value)
    mlflow.set_tag("k_folds", k_folds)
    mlflow.set_tag("scoring", scoring)

    train_dataset, test_dataset, folds = load_dataset(schema, k_folds)
    train, test = train_dataset.df, test_dataset.df

    # !model param needs to be added
    mlflow.log_input(train_dataset, context="training", model=...)
    mlflow.log_input(test_dataset, context="testing", model=...)

    features_pipe = make_text_pipeline(features)

    match method:
        case Method.LOGREG:
            classifier_pipe, param_grid = make_logreg()
        case Method.XGBOOST:
            classifier_pipe, param_grid = make_xgboost()
        case _:
            raise ValueError(f"Method unsupported: {method}")

    mlflow.set_tag("param_grid", param_grid)

    pipe = Pipeline(features_pipe.steps + classifier_pipe.steps)

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
        cv=folds,
        scoring=scoring,
        n_jobs=1,
        verbose=3,
    )

    search.fit(train.text.to_list(), train.label)

    mlflow.log_params(search.best_params_)
    mlflow.log_metric(scoring, search.best_score_)

    log.info("Best params: {}", search.best_params_)
    log.info("Best F1 score: {}", search.best_score_)

    log.info("Evaluating model on the test set")

    y_pred = search.predict(test.text)

    acc = accuracy_score(test.label, y_pred)
    f1 = f1_score(test.label, y_pred)

    mlflow.log_metric("test_accuracy", acc)
    mlflow.log_metric("test_f1", f1)

    log.info("Accuracy: {}", acc)
    log.info("F1 score: {}", f1)

    mlflow.end_run()
