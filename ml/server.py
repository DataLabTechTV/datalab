from dataclasses import dataclass

from fastapi import FastAPI

app = FastAPI()


@dataclass
class Dataset:
    columns: list[str]
    data: list[list]


@app.post("/inference/{model_name}/{model_version}")
async def predict(model_name: str, model_version: str, dataset: Dataset):
    return {
        "model_name": model_name,
        "model_version": model_version,
        "dataset": dataset,
    }
