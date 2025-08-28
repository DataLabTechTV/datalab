import logging

from loguru import logger as log


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = log.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_back and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log.opt(
            depth=depth,
            exception=record.exc_info,
        ).log(
            level,
            record.getMessage(),
        )


def setup_intercept():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    propagate_loggers = (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "asyncio",
        "starlette",
    )

    for logger_name in propagate_loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = []
        logging_logger.propagate = True

    warning_loggers = ("aiokafka",)

    for logger_name in warning_loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.setLevel(logging.WARNING)

    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
