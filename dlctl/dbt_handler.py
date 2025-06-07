import os
from pathlib import Path
from typing import Optional

from dbt.cli.main import dbtRunner
from dbt.contracts.results import RunStatus
from loguru import logger as log

from shared.storage import Storage

DBT_PROJECT_DIR = str((Path(__file__).parents[1] / "transform").resolve())
LOCAL_DIR = str((Path(__file__).parents[1] / "local").resolve())


class DBTHandler:
    def __init__(self, debug: bool = False):
        self.debug = debug

        os.environ["DBT_PROJECT_DIR"] = DBT_PROJECT_DIR
        os.environ["LOCAL_DIR"] = LOCAL_DIR

        s = Storage()
        s.latest_to_env()

    def run(self, models: Optional[tuple[str]] = None):
        dbt = dbtRunner()

        args = ["run"]
        args += ["--project-dir", DBT_PROJECT_DIR]
        args += ["--profiles-dir", DBT_PROJECT_DIR]

        if self.debug:
            args += ["--debug"]

        if models is not None and len(models) > 0:
            args += [
                "--select",
                ",".join(f"{model}" for model in models),
            ]

        result = dbt.invoke(args)

        for r in result.result:
            if r.status == RunStatus.Success:
                log.info("{}: {}", r.node.name, r.status)
            else:
                log.warning("{}: {}", r.node.name, r.status)
