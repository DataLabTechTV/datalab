from enum import Enum
from time import time
from typing import Any, Literal

import pandas as pd
from loguru import logger as log
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from ml.features import Features, make_text_pipeline
from shared.lakehouse import Lakehouse
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
        "xgboost__n_estimators": [100, 200],
        "xgboost__learning_rate": [0.05, 0.1],
        "xgboost__max_depth": [3, 6],
        "xgboost__min_child_weight": [1, 5],
        "xgboost__subsample": [0.8, 1.0],
        "xgboost__colsample_bytree": [0.8, 1.0],
    }

    return pipe, param_grid


def load_dataset(
    schema: str,
    k_folds: Literal[5, 10],
) -> tuple[pd.DataFrame, pd.DataFrame, Folds]:
    lh = Lakehouse()

    train = lh.load_docs_train_set("stage", schema, "dataset", k_folds=k_folds)
    test = lh.load_docs_test_set("stage", schema, "dataset")

    folds = []

    for _, fold in train.groupby("fold_id"):
        test_idx = fold.index.to_list()
        train_idx = list(set(train.index) - set(fold.index))
        folds.append((train_idx, test_idx))

    return train, test, folds


@timed
def train_text_classifier(
    schema: str,
    method: Method,
    features: Features,
    k_folds: Literal[5, 10] = 5,
):
    train, test, folds = load_dataset(schema, k_folds)

    features_pipe = make_text_pipeline(features)

    match method:
        case Method.LOGREG:
            classifier_pipe, param_grid = make_logreg()
        case Method.XGBOOST:
            classifier_pipe, param_grid = make_xgboost()
        case _:
            raise ValueError(f"Method unsupported: {method}")

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
        scoring="f1",
        n_jobs=1,
        verbose=3,
    )

    search.fit(train.text.to_list(), train.label)

    log.info("Best params: {}", search.best_params_)
    log.info("Best F1 score: {}", search.best_score_)

    log.info("Evaluating model on the test set")

    y_pred = search.predict(test.text)

    acc = accuracy_score(test.label, y_pred)
    f1 = f1_score(test.label, y_pred)

    log.info("Accuracy: {}", acc)
    log.info("F1 score: {}", f1)
