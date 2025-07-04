from pathlib import Path

import pytest

from shared.settings import LOCAL_DIR, env


@pytest.fixture(scope="session")
def graph_db_schema():
    db_path = Path(LOCAL_DIR) / env.str("MUSIC_TASTE_GRAPH_DB")

    if not db_path.exists():
        pytest.skip(f"Database not found at {db_path}, skipping test.")

    return "music_taste"
