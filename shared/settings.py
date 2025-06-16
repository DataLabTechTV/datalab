import os
from pathlib import Path

from environs import Env

env = Env()
env.read_env()

LOCAL_DIR = str((Path(__file__).parents[1] / "local").resolve())

MART_SCHEMAS = []

for varname, value in os.environ.items():
    if varname.endswith("_MART_DB"):
        MART_SCHEMAS.append(os.path.splitext(os.path.split(value)[-1])[0])
