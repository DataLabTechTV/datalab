import os
from pathlib import Path
from typing import Optional

from dbt.cli.main import dbtRunner
from dbt.contracts.results import RunStatus
from loguru import logger as log

from shared.settings import LOCAL_DIR, env
from shared.storage import Storage, StoragePrefix

DBT_PROJECT_DIR = str((Path(__file__).parents[1] / "transform").resolve())


class DBTHandler:
    PROJECT_ARGS = []
    PROJECT_ARGS += ["--project-dir", DBT_PROJECT_DIR]
    PROJECT_ARGS += ["--profiles-dir", DBT_PROJECT_DIR]

    def __init__(self, debug: bool = False):
        self.debug = debug

        os.environ["DBT_PROJECT_DIR"] = DBT_PROJECT_DIR
        os.environ["LOCAL_DIR"] = LOCAL_DIR

        s = Storage(prefix=StoragePrefix.INGEST)
        s.latest_to_env()

        self.mkdirs()

        self.dbt = dbtRunner()
        self.deps()

    def mkdirs(self):
        engine_db_dir = os.path.dirname(os.path.join(LOCAL_DIR, env.str("ENGINE_DB")))
        os.makedirs(engine_db_dir, exist_ok=True)

    def deps(self):
        self.dbt.invoke(["deps"] + self.PROJECT_ARGS)

    def run(self, models: Optional[tuple[str, ...]] = None):
        args = ["run"]
        args += self.PROJECT_ARGS

        if self.debug:
            args += ["--debug"]

        if models is not None and len(models) > 0:
            args += [
                "--select",
                ",".join(f"{model}" for model in models),
            ]

        result = self.dbt.invoke(args)

        if result.result is None:
            log.warning("No results returned from dbt")
            return

        for r in result.result:
            if r.status == RunStatus.Success:
                log.info("{}: {}", r.node.name, r.status)
            else:
                log.warning("{}: {}", r.node.name, r.status)

    def test(self, models: Optional[tuple[str, ...]] = None):
        args = ["test"]
        args += self.PROJECT_ARGS

        if self.debug:
            args += ["--debug"]

        if models is not None and len(models) > 0:
            args += [
                "--select",
                ",".join(f"{model}" for model in models),
            ]

        self.dbt.invoke(args)

    def docs_generate(self):
        self.dbt.invoke(["docs", "generate"] + self.PROJECT_ARGS)

    def docs_serve(self):
        self.dbt.invoke(["docs", "serve"] + self.PROJECT_ARGS)
