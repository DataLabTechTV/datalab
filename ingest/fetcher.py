import os
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit, urlunsplit

import requests
from loguru import logger as log
from tqdm import tqdm

from shared.cache import get_requests_cache_session
from shared.storage import Storage, StoragePrefix

DATACITE_API_URL = "https://api.datacite.org/"


class DataCiteFetcher:
    def __init__(self, s3_dir_path: str):
        self.s3_dir_path = s3_dir_path
        self.storage = Storage(StoragePrefix.INGEST)
        self.session = get_requests_cache_session("datacite")

    def to_canonical_doi(self, doi: str) -> str:
        rel_path = urlsplit(doi).path.removeprefix("/")
        canonical_doi = "/".join(rel_path.split("/")[:3])
        return canonical_doi

    def get_url_from_datacite(self, canonical_doi: str) -> str:
        dc_api_url = urljoin(DATACITE_API_URL, f"dois/{canonical_doi}")

        dc_api_resp = self.session.get(dc_api_url)
        dc_api_resp.raise_for_status()

        ds_url = dc_api_resp.json()["data"]["attributes"]["url"]

        return ds_url

    def get_files_list(self, ds_url: str) -> list[tuple[int, str]]:
        ds_url_parts = urlsplit(ds_url)
        ds_persistent_id = parse_qs(ds_url_parts.query)["persistentId"][0]

        ds_api_url = urlunsplit(
            (
                ds_url_parts.scheme,
                ds_url_parts.netloc,
                "/api/datasets/:persistentId",
                f"persistentId={ds_persistent_id}",
                None,
            )
        )

        ds_api_resp = self.session.get(ds_api_url)
        ds_api_resp.raise_for_status()

        ds_files = ds_api_resp.json()["data"]["latestVersion"]["files"]

        files = []

        for ds_file in ds_files:
            if "dataFile" not in ds_file:
                continue

            file_id = ds_file["dataFile"]["id"]
            filename = ds_file["dataFile"]["filename"]

            files.append((file_id, filename))

        return files

    def download_file(self, ds_url: str, file_id: int) -> str:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            ds_url_parts = urlsplit(ds_url)

            ds_api_url = urlunsplit(
                (
                    ds_url_parts.scheme,
                    ds_url_parts.netloc,
                    f"/api/access/datafile/{file_id}",
                    None,
                    None,
                )
            )

            log.info("Downloading {} to {}", file_id, ds_api_url, tmp.name)

            # Uncached here
            with requests.get(ds_api_url, stream=True) as r:
                r.raise_for_status()

                total_size = int(r.headers.get("content-length", 0))

                with (
                    open(tmp.name, "wb") as fp,
                    tqdm(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=tmp.name,
                    ) as pb,
                ):
                    for chunk in r.iter_content(chunk_size=262144):
                        if chunk is not None:
                            fp.write(chunk)
                            pb.update(len(chunk))

            return tmp.name

    def download(self, doi: str, target: Path):
        log.info("Processing DOI: {}", doi)

        canonical_doi = self.to_canonical_doi(doi)
        ds_url = self.get_url_from_datacite(canonical_doi)

        log.info("Getting files from {}", ds_url)
        files = self.get_files_list(ds_url)

        for file_id, filename in files:
            try:
                tmp_path = self.download_file(ds_url, file_id)
                self.storage.upload_file(tmp_path, f"{target}/{filename}")
            finally:
                os.unlink(tmp_path)
