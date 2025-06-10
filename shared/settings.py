from pathlib import Path

from environs import Env

env = Env()
env.read_env()

LOCAL_DIR = str((Path(__file__).parents[1] / "local").resolve())
