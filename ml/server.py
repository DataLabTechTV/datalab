from contextlib import asynccontextmanager
from dataclasses import dataclass
from threading import Thread

import mlflow
import pandas as pd
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from mlflow.exceptions import RestException

from ml.events import consumer_loop

app = FastAPI()
models = {}


@dataclass
class Dataset:
    columns: list[str]
    data: list[list]
    log_to_lakehouse: bool = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    thread = Thread(target=consumer_loop, daemon=True)
    thread.start()

    yield

    thread.join()


@app.post("/inference/{model_name}/{model_version}")
async def predict(model_name: str, model_version: str, dataset: Dataset):
    model_uri = f"models:/{model_name}/{model_version}"

    if model_uri not in models:
        try:
            models[model_uri] = mlflow.pyfunc.load_model(model_uri)
        except RestException as e:
            return JSONResponse(
                {"error": "Model not found"},
                status_code=status.HTTP_404_NOT_FOUND,
            )

    data = pd.DataFrame(dataset.data, columns=dataset.columns)
    pred = models[model_uri].predict(data)

    return {
        "model_name": model_name,
        "model_version": model_version,
        "predictions": pred.tolist(),
    }


# TODO: A/B testing request
