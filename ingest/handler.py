from loguru import logger as log
from slugify import slugify

from ingest.storage import Storage


def handle_standalone(dataset: str):
    ds_name = slugify(dataset, separator="_")
    log.info("Standalone detected, creating dataset: {}", ds_name)

    try:
        s = Storage()
        s3_dir_path = s.mkdir(ds_name, dated=True)
        s.set_latest(ds_name, s3_dir_path)
    except:
        log.exception("Could not create directory {} for {}", ds_name, dataset)
