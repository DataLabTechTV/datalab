from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import Enum
from typing import Sequence

import pandas as pd

InferenceInput = str | Sequence[float]
InferenceOutput = float


class InferenceProducerType(Enum):
    RESULT = 1
    FEEDBACK = 2


@dataclass
class InferenceModel:
    name: str
    version: str


@dataclass
class InferenceRequest:
    models: list[InferenceModel] | InferenceModel
    data: InferenceInput
    log_to_lakehouse: bool = False

    def get_input(self) -> pd.DataFrame:
        data = [self.data] if type(self.data) is str else self.data
        return pd.Series(data, name="input").to_frame()


@dataclass
class InferenceResult:
    inference_uuid: str
    model: InferenceModel
    data: InferenceInput
    prediction: float
    created_at: int = int(datetime.now(timezone.utc).timestamp()) * 1_000_000

    @classmethod
    def from_dict(cls, data: dict):
        field_names = {f.name for f in fields(cls)}

        field_data = {}

        for k, v in data.items():
            if k not in field_names:
                continue

            match k:
                case "model":
                    field_data[k] = InferenceModel(**v)
                case _:
                    field_data[k] = v

        return cls(**field_data)


@dataclass
class InferenceFeedback:
    inference_uuid: str
    feedback: float
