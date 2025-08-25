from dataclasses import dataclass
from typing import Self
from urllib.parse import urlparse

from shared.utils import fn_sanitize


@dataclass
class DatasetURL:
    author: str
    slug: str
    handle: str
    name: str

    @classmethod
    def parse(cls, dataset_url: str) -> Self:
        url = urlparse(dataset_url)
        path = url.path.split("/")

        author = path[-2]
        slug = path[-1]
        handle = f"{author}/{slug}"
        name = fn_sanitize(slug)

        ds_url = cls(
            author=author,
            slug=slug,
            handle=handle,
            name=name,
        )

        return ds_url
