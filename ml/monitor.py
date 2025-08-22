import functools
from datetime import datetime
from enum import Flag, auto

import numpy as np
import numpy.typing as npt
import pandas as pd
from loguru import logger as log
from scipy.stats import entropy
from slugify import slugify

from ml.inference import load_model
from ml.types import InferenceModel
from shared.lakehouse import Lakehouse


class MonitoringStats(Flag):
    COUNT = auto()
    PREDICTION_DRIFT = auto()
    FEATURE_DRIFT = auto()
    DATA_DRIFT = auto()
    ESTIMATED_PERFORMANCE = auto()
    DATA_QUALITY = auto()

    ALL = (
        COUNT
        | PREDICTION_DRIFT
        | FEATURE_DRIFT
        | DATA_DRIFT
        | ESTIMATED_PERFORMANCE
        | DATA_QUALITY
    )


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

    def _to_inference_model(self, model_uri: str) -> InferenceModel:
        _, name, version, *_ = model_uri.split("/")
        return InferenceModel(name=name, version=version)

    def _to_column_name(self, model_uri: str) -> str:
        im = self._to_inference_model(model_uri)
        column_name = slugify(f"{im.name}_{im.version}", separator="_")
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

        self.inferences["date"] = self.inferences.created_at.dt.date

        self.inferences["model_uri"] = (
            "models:/"
            + self.inferences.model_name
            + "/"
            + self.inferences.model_version
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

        self.stats = (
            pd.DataFrame(index=date_idx, columns=columns)
            .rename_axis("date", axis=0)
            .rename_axis(["model_uri", "stat"], axis=1)
        )

    def _compute_count(self):
        count_stats = (
            self.inferences[["date", "model_uri", "inference_uuid"]]
            .groupby(["date", "model_uri"])
            .count()
            .rename(columns={"inference_uuid": "count"})
            .reset_index()
            .pivot(index="date", columns="model_uri")
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
        model_hist = {}

        for model_uri in self.model_uris:
            model_column = self._to_column_name(model_uri)

            hist_ref, _ = np.histogram(
                self.dataset[model_column],
                bins=bins,
                density=True,
            )

            model_hist[model_uri] = hist_ref

        def prediction_drift(model_uri: str, data: npt.NDArray):
            hist_ref = model_hist[model_uri]
            hist_curr, _ = np.histogram(data, bins=bins, density=True)

            prediction_drift_kl = entropy(hist_ref + epsilon, hist_curr + epsilon)

            return prediction_drift_kl

        prediction_drift_stats = (
            self.inferences.set_index(self.inferences.created_at.dt.floor("D"))
            .rename_axis("date")
            .sort_index()
            .groupby("model_uri")["prediction"]
            .rolling(window=pd.Timedelta(days=self.window_size), min_periods=1)
            .apply(functools.partial(prediction_drift, model_uri))
            .reset_index()
            .rename(columns={"prediction": "pred_drift"})
            .drop_duplicates(subset=["date", "model_uri"])
            .pivot(index="date", columns="model_uri")
            .swaplevel(axis=1)
            .rename_axis(["model_uri", "stat"], axis=1)
        )

        self.stats = self.stats.merge(
            prediction_drift_stats,
            how="left",
            left_index=True,
            right_index=True,
        )

    def _compute_feature_drift(self):
        pass

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

        if MonitoringStats.FEATURE_DRIFT in self.flags:
            self._compute_feature_drift()

        if MonitoringStats.DATA_DRIFT in self.flags:
            self._compute_data_drift()

        if MonitoringStats.ESTIMATED_PERFORMANCE in self.flags:
            self._compute_estimated_performance()

        if MonitoringStats.DATA_QUALITY in self.flags:
            self._compute_data_quality()

    def store(self):
        pass
