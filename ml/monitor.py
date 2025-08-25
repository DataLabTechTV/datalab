import functools
import json
from datetime import datetime
from enum import Flag, auto
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import scipy
from loguru import logger as log
from scipy.stats import ks_2samp
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from slugify import slugify
from tqdm import tqdm

from ml.inference import load_model
from ml.types import InferenceModel
from shared.color import COLOR_PALETTE
from shared.lakehouse import Lakehouse
from shared.settings import LOCAL_DIR


class MonitoringStats(Flag):
    COUNT = auto()
    PREDICTION_DRIFT = auto()
    FEATURE_DRIFT = auto()
    ESTIMATED_PERFORMANCE = auto()
    USER_EVALUATION = auto()

    ALL = (
        COUNT
        | PREDICTION_DRIFT
        | FEATURE_DRIFT
        | ESTIMATED_PERFORMANCE
        | USER_EVALUATION
    )


class Monitoring:
    def __init__(
        self,
        schema: str,
        model_uris: list[str],
        since: datetime | None,
        until: datetime | None,
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

    def _compute_prediction_drift(self):
        log.info("Computing prediction drift over time")

        def prediction_drift(model_uri: str, current: pd.Series):
            reference = self.dataset[self._to_column_name(model_uri)]
            ks_result = ks_2samp(reference, current)
            return ks_result.statistic

        def rolling_prediction_drift(predictions: pd.Series):
            model_uri = predictions.name

            rolling_predictions_drift_stats = predictions.rolling(
                window=pd.Timedelta(days=self.window_size),
                min_periods=1,
            ).apply(
                functools.partial(
                    prediction_drift,
                    model_uri,
                )
            )

            return rolling_predictions_drift_stats

        prediction_drift_stats = (
            self.inferences.set_index(self.inferences.created_at.dt.floor("D"))
            .rename_axis("date")
            .sort_index()
            .groupby("model_uri", group_keys=True)["prediction"]
            .apply(rolling_prediction_drift)
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
        log.info("Computing feature drift over time")

        def features_drift(reference: pd.DataFrame, current: pd.DataFrame):
            ref_dataset = pd.DataFrame(reference)
            ref_dataset["target"] = 0

            cur_dataset = pd.DataFrame(current)
            cur_dataset["target"] = 1

            dataset = pd.concat((ref_dataset, cur_dataset))

            X_train, X_test, y_train, y_test = train_test_split(
                dataset.drop(columns="target"),
                dataset.target,
                test_size=0.3,
                stratify=dataset.target,
            )

            model = LogisticRegression()
            model.fit(X_train, y_train)

            pos_class_idx = model.classes_.tolist().index(1)
            y_pred_proba = model.predict_proba(X_test)[:, pos_class_idx]
            score = roc_auc_score(y_test, y_pred_proba)

            return score

        def rolling_features_drift(data: pd.Series):
            model_uri = data.name
            model = load_model(model_uri)

            input_data = pd.DataFrame(data.apply(json.loads).tolist())
            if input_data.shape[1] == 1:
                input_data = input_data.iloc[:, 0]

            # All steps except the classifier (last one)
            pipeline = model[:-1]

            reference_features = pipeline.transform(self.dataset.input)
            current_features = pipeline.transform(input_data)

            if isinstance(reference_features, scipy.sparse.spmatrix):
                reference = pd.DataFrame.sparse.from_spmatrix(reference_features)
                current = pd.DataFrame.sparse.from_spmatrix(
                    current_features,
                    index=data.index,
                )
            else:
                reference = pd.DataFrame(reference_features)
                current = pd.DataFrame(current_features, index=data.index)

            rolling_features_drift_stats = []

            for end_time in tqdm(current.index.drop_duplicates(), desc="Days"):
                current_window = current.loc[
                    end_time
                    - pd.Timedelta(days=self.window_size)
                    + pd.Timedelta("1D") : end_time
                ]

                score = features_drift(reference, current_window)
                rolling_features_drift_stats.append(pd.Series(score, name=end_time))

            rolling_features_drift_stats = (
                pd.DataFrame(rolling_features_drift_stats)
                .rename(columns={0: "feat_drift"})
                .rename_axis("date")
            )

            return rolling_features_drift_stats

        features_drift_stats = (
            self.inferences.set_index(self.inferences.created_at.dt.floor("D"))
            .rename_axis("date")
            .sort_index()
            .groupby("model_uri", group_keys=True)["data"]
            .apply(rolling_features_drift)
            .reset_index()
            .pivot(index="date", columns="model_uri")
            .swaplevel(axis=1)
            .rename_axis(["model_uri", "stat"], axis=1)
        )

        self.stats = self.stats.merge(
            features_drift_stats,
            how="left",
            left_index=True,
            right_index=True,
        )

    def _compute_estimated_performance(self, decision_threshold: float = 0.5):
        log.info("Computing estimated performance over time using CBPE")

        cbpe_models = {}

        for model_uri in self.model_uris:
            p_ref = self.dataset[self._to_column_name(model_uri)]

            y_ref = self.dataset.target
            y_hat_ref = (p_ref >= decision_threshold).astype(float)
            correctness_ref = (y_hat_ref == y_ref).astype(float)

            cbpe_models[model_uri] = IsotonicRegression(out_of_bounds="clip")
            cbpe_models[model_uri].fit(p_ref, correctness_ref)

        def cbpe_metrics(model_uri: str, metric: str, current: pd.Series):
            epsilon = 1e-12

            p_cur = current
            y_hat_cur = (p_cur >= decision_threshold).astype(float)

            est_correctness = cbpe_models[model_uri].predict(p_cur)

            match metric.lower():
                case "accuracy":
                    e_accuracy = np.mean(est_correctness)
                    return e_accuracy
                case "f1":
                    TP = np.sum(est_correctness * (y_hat_cur == 1.0))
                    FP = np.sum((1 - est_correctness) * (y_hat_cur == 1.0))
                    FN = np.sum((1 - est_correctness) * (y_hat_cur == 0.0))

                    precision = TP / (TP + FP + epsilon)
                    recall = TP / (TP + FN + epsilon)
                    e_f1 = 2 * precision * recall / (precision + recall + epsilon)

                    return e_f1
                case _:
                    return -1.0

        def rolling_cbpe_metrics(metric: str, predictions: pd.Series):
            model_uri = predictions.name

            rolling_cbpe_metrics_stats = (
                predictions.rolling(
                    window=pd.Timedelta(days=self.window_size),
                    min_periods=1,
                )
                .apply(
                    functools.partial(
                        cbpe_metrics,
                        model_uri,
                        metric,
                    )
                )
                .groupby("date")
                .mean()
            )

            return rolling_cbpe_metrics_stats

        cbpe_stats = (
            self.inferences.set_index(self.inferences.created_at.dt.floor("D"))
            .rename_axis("date")
            .sort_index()
            .groupby("model_uri", group_keys=True)["prediction"]
            .apply(functools.partial(rolling_cbpe_metrics, "accuracy"))
            .reset_index()
            .rename(columns={"prediction": "e_f1"})
            .pivot(index="date", columns="model_uri")
            .swaplevel(axis=1)
            .rename_axis(["model_uri", "stat"], axis=1)
        )

        self.stats = self.stats.merge(
            cbpe_stats,
            how="left",
            left_index=True,
            right_index=True,
        )

    def _compute_user_evaluation(self):
        user_eval_stats = self.inferences[
            (~self.inferences.feedback.isna()) & (len(self.inferences.feedback) > 0)
        ].copy()

        user_eval_stats["user_brier"] = user_eval_stats.apply(
            lambda row: np.square(row.prediction - row.feedback.mean()),
            axis=1,
        )

        user_eval_stats = (
            user_eval_stats.groupby(
                [
                    "model_uri",
                    "date",
                ]
            )["user_brier"]
            .mean()
            .reset_index()
            .pivot(index="date", columns="model_uri")
            .swaplevel(axis=1)
        )

        self.stats = self.stats.merge(
            user_eval_stats,
            how="left",
            left_index=True,
            right_index=True,
        )

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

        if MonitoringStats.ESTIMATED_PERFORMANCE in self.flags:
            self._compute_estimated_performance()

        if MonitoringStats.USER_EVALUATION in self.flags:
            self._compute_user_evaluation()

    def store(self):
        self.lh.ml_monitoring_store(self.schema, self.stats)

    def load(self):
        self.stats = self.lh.ml_monitoring_load(self.schema)

    def plot(self):
        output_dir = Path(LOCAL_DIR) / "monitor"
        output_dir.mkdir(parents=True, exist_ok=True)

        data = self.stats.copy()

        data["model"] = data.model_name + " (" + data.model_version + ")"
        data = data.drop(columns=["model_name", "model_version"])

        metric_names = {
            "count": "Number of Inferences Over Time",
            "pred_drift": "Prediction Shift (KS D-Statistic)",
            "feat_drift": "Feature Drift (ROC AUC)",
            "e_f1": "Estimated F1-Score Based on CBPE",
            "e_accuracy": "Estimated Accuracy Based on CBPE",
            "user_brier": "Mean Brier Score Based on Avg. User Feedback",
        }

        metrics = list(set(data.columns) & set(metric_names.keys()))

        data = data[["date", "model"] + metrics].pivot(
            index="date",
            columns="model",
            values=metrics,
        )

        plt.rcParams["axes.prop_cycle"] = plt.cycler(color=COLOR_PALETTE)

        for metric in metrics:
            output_path = output_dir / f"{metric}.png"
            metric_name = metric_names[metric]

            log.info("Plotting {} into {}", metric_name, output_path)

            fig, ax = plt.subplots(figsize=(7, 3.5), dpi=300)

            data[metric].plot.bar(ax=ax, rot=0, xlabel="")

            step = 7
            ax.set_xticks(range(0, len(data[metric]), step))
            ax.set_xticklabels(data[metric].index[::step].strftime("%d %b %Y"))

            plt.xticks(ha="left")

            plt.legend(
                title=None,
                ncol=2,
                loc="upper left",
                bbox_to_anchor=(0, -0.175),
                borderaxespad=0,
            )

            plt.title(metric_name)
            plt.tight_layout()

            fig.savefig(output_path)
