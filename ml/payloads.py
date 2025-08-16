from dataclasses import dataclass


@dataclass
class InferenceDataset:
    columns: list[str]
    data: list[list]
    log_to_lakehouse: bool = False


@dataclass
class InferenceResultPayload:
    inference_uuid: str
    model_name: str
    model_version: str
    dataset: InferenceDataset
    predictions: list[bool] | list[int] | list[float]
