import asyncio
import random
from uuid import uuid4

import mlflow
import pandas as pd
from joblib import Memory
from loguru import logger as log
from mlflow.exceptions import RestException

from ml.types import InferenceModel, InferenceRequest, InferenceResult
from shared.cache import get_cache_dir

memory = Memory(get_cache_dir() / "ml/models", verbose=0)
memory.clear(warn=False)


class ModelNotFound(Exception):
    pass


@memory.cache
def load_model(model_uri: str):
    try:
        return mlflow.sklearn.load_model(model_uri)
    except RestException:
        raise ModelNotFound(model_uri)


def predict(inference_request: InferenceRequest) -> InferenceResult:
    if type(inference_request.models) is InferenceModel:
        inference_model = inference_request.models
    else:
        log.debug("Randomly selecting a model")
        inference_model = random.choice(inference_request.models)

    model_uri = f"models:/{inference_model.name}/{inference_model.version}"
    model = load_model(model_uri)

    log.info("Running inference using {}", model_uri)

    data = inference_request.get_input()
    prediction = model.predict_proba(data)[0, 0].item()

    inference_result = InferenceResult(
        inference_uuid=str(uuid4()),
        model=inference_model,
        data=inference_request.data,
        prediction=prediction,
    )

    return inference_result
