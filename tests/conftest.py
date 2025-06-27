import sys

from loguru import logger


def pytest_configure(config):
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
