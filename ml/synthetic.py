import itertools
from datetime import datetime

import numpy as np
from faker import Faker
from loguru import logger as log
from tqdm import tqdm

import ml.inference
from ml.inference import predict
from ml.types import InferenceFeedback, InferenceModel, InferenceRequest
from shared.lakehouse import Lakehouse


def simulate_inference(
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
    inference_models: list[InferenceModel] | InferenceModel,
    batch_size: int = 100,
):
    lh = Lakehouse(in_memory=True)
    dataset = lh.ml_load_dataset("stage", schema, "monitor")
    dataset = dataset.sample(frac=sample_fraction)

    inference_uuids = []
    faker = Faker()
    inference_results = []
    total = len(dataset)
    batches = itertools.batched(dataset.itertuples(index=False), batch_size)

    log.disable(ml.inference.__name__)

    for batch_nr, batch in enumerate(batches, 1):
        count = 0
        inference_results = []

        for row in tqdm(batch, total=len(batch), desc=f"Batch {batch_nr}"):
            inference_request = InferenceRequest(
                models=inference_models,
                data=row.input,
            )

            inference_result = predict(inference_request)

            random_date = faker.date_time_between(min_date, max_date)
            inference_result.created_at = int(random_date.timestamp()) * 1_000_000

            inference_uuids.append(inference_result.inference_uuid)

            inference_results.append(inference_result)

            count += 1

        log.info("Inferences run so far: {}/{}", count, total)
        lh.ml_inference_insert_results(schema, inference_results)

    log.enable(ml.inference.__name__)

    dataset["inference_uuid"] = inference_uuids

    for n in range(passes):
        feedback_frac = np.random.uniform(min_feedback_fraction, max_feedback_fraction)
        wrong_frac = np.random.uniform(min_wrong_fraction, max_wrong_fraction)

        log.info(
            "Starting feedback pass nr. {} (frac={}, wrong={})",
            n,
            feedback_frac,
            wrong_frac,
        )

        feedback = dataset.sample(frac=feedback_frac)

        wrong_size = int(np.ceil(len(feedback) * wrong_frac))
        wrong_pos = np.random.randint(0, len(feedback), wrong_size)
        wrong_idx = feedback.iloc[wrong_pos].index
        feedback.loc[wrong_idx, "target"] = 1 - feedback.loc[wrong_idx, "target"]

        inference_feedback = []

        for row in feedback.itertuples(index=False):
            inference_feedback.append(
                InferenceFeedback(
                    inference_uuid=row.inference_uuid,
                    feedback=float(row.target >= decision_threshold),
                )
            )

        lh.ml_inference_append_feedback(schema, inference_feedback)
