from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit, urlunsplit

from loguru import logger as log

from shared.cache import get_requests_cache_session

DATACITE_API_URL = "https://api.datacite.org/"


class DataCiteFetcher:
    def __init__(self):
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

    def get_files(self, ds_url: str) -> dict[int, str]:
        ds_url_parts = urlsplit(ds_url)
        ds_persistent_id = parse_qs(ds_url_parts.query)["persistentId"][0]

        ds_api_url = urlunsplit(
            (
                ds_url_parts.scheme,
                ds_url_parts.netloc,
                "/api/datasets/:persistentId",
                f"persistentId={ds_persistent_id}",
                "",
            )
        )

        ds_api_resp = self.session.get(ds_api_url)
        ds_files = ds_api_resp.json()["data"]["latestVersion"]["files"]

        files = {}

        for ds_file in ds_files:
            if "dataFile" not in ds_file:
                continue

            file_id = ds_file["dataFile"]["id"]
            filename = ds_file["dataFile"]["filename"]

            files[file_id] = filename

        return files

    def download(self, doi: str, target: Path):
        log.info("Processing DOI: {}", doi)

        canonical_doi = self.to_canonical_doi(doi)
        ds_url = self.get_url_from_datacite(canonical_doi)

        files = self.get_files(ds_url)

        for file_id, filename in files.items():
            download_url = ...
            print(file_id, filename)
