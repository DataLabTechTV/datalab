import shutil
from pathlib import Path
from typing import Optional

import humanize
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


def cache_usage():
    log.info("Calculating cache usage statistics")

    cache_dir = get_cache_dir()

    total_size_bytes = 0
    byte_size_per_dir = {}

    for path in cache_dir.iterdir():
        if path.is_dir():
            dir_name = f"{path.relative_to(cache_dir)}/"

            byte_size_per_dir[dir_name] = sum(
                f.stat().st_size for f in path.rglob("*") if f.is_file()
            )

            total_size_bytes += byte_size_per_dir[dir_name]

        elif path.is_file():
            total_size_bytes += path.stat().st_size

    print("Total:", humanize.naturalsize(total_size_bytes))

    for dir_name, dir_size in byte_size_per_dir.items():
        print(f"\t{dir_name}", humanize.naturalsize(dir_size))
