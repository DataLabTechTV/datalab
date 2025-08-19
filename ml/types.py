from dataclasses import dataclass


@dataclass
class InferenceDataset:
    columns: list[str]
    data: list[list]


@dataclass
class InferenceModel:
    name: str
    version: str


@dataclass
class InferenceRequest:
    models: list[InferenceModel] | InferenceModel
    dataset: InferenceDataset
    log_to_lakehouse: bool = False


@dataclass
class InferenceResult:
    inference_uuid: str
    model_name: str
    model_version: str
    dataset: InferenceDataset
    predictions: list[bool] | list[int] | list[float]
