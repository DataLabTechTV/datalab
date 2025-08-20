from datetime import datetime

import numpy as np
from loguru import logger as log
from tqdm import tqdm

import ml.inference
from ml.inference import predict
from ml.types import InferenceModel, InferenceRequest
from shared.lakehouse import Lakehouse


async def simulate_inference(
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
):
    lh = Lakehouse(in_memory=True)
    dataset = lh.ml_load_dataset("stage", schema, "monitor")
    dataset = dataset.sample(frac=sample_fraction)

    inference_results = []

    log.disable(ml.inference.__name__)

    for row in tqdm(dataset.itertuples(index=False), total=len(dataset)):
        inference_request = InferenceRequest(
            models=inference_models,
            data=row.input,
        )

        inference_result = predict(inference_request)
        inference_results.append(inference_result)

    log.enable(ml.inference.__name__)

    lh.ml_inference_insert_results(schema, inference_results)

    # for n in range(passes):
    #     log.info("Starting pass nr. {}", n)

    #     feedback_frac = np.random.uniform(min_feedback_fraction, max_feedback_fraction)

    #     wrong_frac = np.random.uniform(min_wrong_fraction, max_wrong_fraction)
