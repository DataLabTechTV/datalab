from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterator, Optional, Self


class DatasetTemplateID(Enum):
    THE_ATLAS_OF_ECONOMIC_COMPLEXITY = "atlas"


@dataclass
class DatasetFileMetadata:
    def __init__(
        self,
        source: str,
        target: str | Path,
        attribution: Optional[str] = None,
    ):
        self.source = source

        if isinstance(target, Path):
            self.target = target
        elif isinstance(target, str):
            self.target = Path(target)
        else:
            raise TypeError("Invalid type: target must either be a Path or a str")

        self.attribution = attribution

    def __iter__(self):
        yield self.source
        yield self.target
        yield self.attribution


class DatasetTemplate(ABC):
    @classmethod
    def from_id(cls, template_id: DatasetTemplateID) -> Self:
        """Instance child classes based on the DatasetTemplateID"""
        match template_id:
            case DatasetTemplateID.THE_ATLAS_OF_ECONOMIC_COMPLEXITY:
                from ingest.template.atlas import TheAtlasOfEconomicComplexityTemplate

                return TheAtlasOfEconomicComplexityTemplate()

    def __iter__(self) -> Iterator[DatasetFileMetadata]:
        """Iterate over the dataset files in the template."""
        yield from self.template

    @property
    @abstractmethod
    def template(self) -> list[DatasetFileMetadata]:
        """
        Source and target metadata for dataset files.


        - The source might be a filename, a URL, a table name, etc.
        - The target will be a destination dir Path where the source should be dropped.
        - Attribution is used to comply with legal requirements and will be printed whenever the dataset file is accessed.
        """


class DataCiteTemplate(DatasetTemplate):
    pass
