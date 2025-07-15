import shutil
from pathlib import Path
from typing import Optional

from loguru import logger as log
from platformdirs import user_cache_dir
from requests_cache.session import CachedSession


def get_cache_dir() -> Path:
    cache_dir = Path(user_cache_dir("datalab"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_requests_cache_session(name: str) -> CachedSession:
    cache_dir = get_cache_dir() / "requests" / name
    session = CachedSession(cache_name=cache_dir, backend="filesystem")
    return session


def expunge_cache(namespace: Optional[str] = None, name: Optional[str] = None):
    cache_dir = get_cache_dir()

    match (namespace, name):
        case (None, None):
            log.info("Cleaning cache completely")
            shutil.rmtree(cache_dir)
        case (_, None):
            log.info("Cleaning cache for {}", namespace)
            shutil.rmtree(cache_dir / namespace)
        case (None, _):
            raise ValueError("name requires namespace to be set")
        case _:
            log.info("Cleaning cache for {}: {}", namespace, name)
            shutil.rmtree(cache_dir / namespace / name)
