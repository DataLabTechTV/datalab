from datetime import datetime
from enum import Flag, auto

import numpy as np
import pandas as pd
from loguru import logger as log
from scipy.stats import entropy
from slugify import slugify

from ml.inference import load_model
from shared.lakehouse import Lakehouse


class MonitoringStats(Flag):
    COUNT = auto()
    PREDICTION_DRIFT = auto()
    DATA_DRIFT = auto()
    ESTIMATED_PERFORMANCE = auto()
    DATA_QUALITY = auto()
    ALL = COUNT | PREDICTION_DRIFT | DATA_DRIFT | ESTIMATED_PERFORMANCE | DATA_QUALITY


class Monitoring:
    def __init__(
        self,
        schema: str,
        model_uris: list[str],
        since: datetime,
        until: datetime,
        window_size: int = 7,
        flags: MonitoringStats = MonitoringStats.ALL,
    ):
        self.schema = schema
        self.model_uris = model_uris
        self.since = since
        self.until = until
        self.window_size = window_size
        self.flags = flags

        self.lh = Lakehouse(in_memory=True)

        self.model_columns = list(map(self._to_column_name, model_uris))
        self.dataset = None
        self.inferences = None
        self.stats = None

    def _to_column_name(self, model_uri: str) -> str:
        _, name, version, *_ = model_uri.split("/")
        column_name = slugify(f"{name}_{version}", separator="_")
        return column_name

    def _load_data(self):
        self.dataset = self.lh.ml_load_dataset(
            catalog="stage",
            schema=self.schema,
            table_name="dataset",
        )

        self.inferences = self.lh.ml_load_inferences(
            catalog="secure_stage",
            schema=self.schema,
            table_name="inference_results",
            since=self.since,
            until=self.until,
        )

    def _ensure_predictions(self):
        for model_uri in self.model_uris:
            log.info("Ensuring training set predictions for {}", model_uri)

            model_column = self._to_column_name(model_uri)

            if model_column not in self.dataset.columns:
                model = load_model(model_uri)
                pos_class_idx = model.classes_.tolist().index(1)
                predictions = model.predict_proba(self.dataset.input)[:, pos_class_idx]
                self.dataset[model_column] = predictions

    def _init_stats(self):
        date_idx = pd.date_range(
            start=self.inferences.created_at.min(),
            end=self.inferences.created_at.max(),
        ).date

        columns = pd.MultiIndex.from_product([self.model_uris, []])

        self.stats = pd.DataFrame(index=date_idx, columns=columns)

    def _compute_count(self):
        model_uris = pd.Series(
            "models:/"
            + self.inferences.model_name
            + "/"
            + self.inferences.model_version,
            name="model_uri",
        )

        count_stats = (
            self.inferences[["inference_uuid"]]
            .groupby([self.inferences.created_at.dt.date, model_uris])
            .count()
            .rename(columns={"inference_uuid": "count"})
            .reset_index()
            .pivot(index="created_at", columns="model_uri")
            .swaplevel(axis=1)
            .fillna(0)
        )

        self.stats = self.stats.merge(
            count_stats,
            how="left",
            left_index=True,
            right_index=True,
        )

    def _compute_prediction_drift(self, bins: int = 20, epsilon: float = 1e-8):
        for model_uri in self.model_uris:
            _, name, version, *_ = model_uri.split("/")
            model_column = self._to_column_name(model_uri)

            hist_ref, _ = np.histogram(
                self.dataset[model_column],
                bins=bins,
                density=True,
            )

            hist_curr, _ = np.histogram(
                self.inferences.loc[
                    (self.inferences.model_name == name)
                    & (self.inferences.model_version == version),
                    "prediction",
                ],
                bins=bins,
                density=True,
            )

            prediction_drift_kl = entropy(hist_ref + epsilon, hist_curr + epsilon)
            # TODO: finish implementation

    def _compute_data_drift(self):
        pass

    def _compute_estimated_performance(self):
        pass

    def _compute_data_quality(self):
        pass

    def compute(self):
        self._load_data()
        self._ensure_predictions()
        self._init_stats()

        if MonitoringStats.COUNT in self.flags:
            self._compute_count()

        if MonitoringStats.PREDICTION_DRIFT in self.flags:
            self._compute_prediction_drift()

        if MonitoringStats.DATA_DRIFT in self.flags:
            self._compute_data_drift()

        if MonitoringStats.ESTIMATED_PERFORMANCE in self.flags:
            self._compute_estimated_performance()

        if MonitoringStats.DATA_QUALITY in self.flags:
            self._compute_data_quality()

    def store(self):
        pass
