import time
from datetime import timedelta
from functools import wraps

import inflection
from anyascii import anyascii
from loguru import logger as log
from slugify import slugify


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.perf_counter()
        self.elapsed = timedelta(seconds=self.end - self.start)
        log.info(f"Elapsed time: {self.elapsed}")


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with Timer():
            result = func(*args, **kwargs)
            return result

    return wrapper


def fn_sanitize(filename: str, separator: str = "_"):
    return slugify(
        inflection.underscore(
            anyascii(filename),
        ),
        separator=separator,
    )
