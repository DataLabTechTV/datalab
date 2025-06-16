import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import git
import kagglehub as kh
from loguru import logger as log
from platformdirs import user_cache_dir
from slugify import slugify

from shared.storage import Storage, StoragePrefix


def handle_standalone(dataset: str):
    ds_name = slugify(dataset, separator="_")
    log.info("Standalone detected, creating dataset: {}", ds_name)

    try:
        s = Storage(prefix=StoragePrefix.INGEST)
        s3_dir_path = s.get_dir(ds_name, dated=True, upload_placeholder=True)
        s.upload_manifest(ds_name, latest=s3_dir_path)
    except Exception as e:
        log.error("Could not create directory {} for {}: {}", ds_name, dataset, e)


@dataclass
class DatasetURL:
    author: str
    slug: str
    handle: str
    name: str


def parse_dataset_url(dataset_url: str) -> DatasetURL:
    url = urlparse(dataset_url)
    path = url.path.split("/")

    author = path[-2]
    slug = path[-1]
    handle = f"{author}/{slug}"
    name = slugify(slug, separator="_")

    ds_url = DatasetURL(
        author=author,
        slug=slug,
        handle=handle,
        name=name,
    )

    return ds_url


def handle_kaggle(dataset_url: str):
    ds_url = parse_dataset_url(dataset_url)
    log.info("Kaggle dataset detected, downloading dataset: {}", ds_url.name)

    try:
        kaggle_ds_path = kh.dataset_download(ds_url.handle)
        s = Storage(prefix=StoragePrefix.INGEST)
        s3_dir_path = s.get_dir(ds_url.name, dated=True)
        s.upload_dir(source_path=kaggle_ds_path, s3_target_path=s3_dir_path)
        s.upload_manifest(ds_url.name, latest=s3_dir_path)
    except:
        log.exception(
            "Couldn't download dataset. You might need to setup "
            "~/.config/kaggle/kaggle.json via 'Create New Token' "
            "under API on https://www.kaggle.com/settings"
        )


def get_cache_dir() -> Path:
    cache_dir = Path(user_cache_dir("datalab"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def handle_hugging_face(dataset_url: str):
    ds_url = parse_dataset_url(dataset_url)
    log.info("Hugging Face dataset detected, downloading dataset: {}", ds_url.name)

    try:
        hf_ds_path = get_cache_dir() / ds_url.author / ds_url.slug

        log.info("Fetching {}", dataset_url)

        if not hf_ds_path.exists():
            log.info("Cloning {}", dataset_url)
            git.Repo.clone_from(dataset_url, hf_ds_path)

            log.info("Deleting .git* files: {}", hf_ds_path)
            for git_file_path in hf_ds_path.glob(".git*"):
                if git_file_path.is_dir():
                    shutil.rmtree(git_file_path)
                else:
                    git_file_path.unlink()

        s = Storage(prefix=StoragePrefix.INGEST)
        s3_dir_path = s.get_dir(ds_url.name, dated=True)
        s.upload_dir(source_path=hf_ds_path, s3_target_path=s3_dir_path)
        s.upload_manifest(ds_url.name, latest=s3_dir_path)
    except Exception as e:
        log.exception("Couldn't download dataset: {}", e)
