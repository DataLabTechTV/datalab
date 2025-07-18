import tempfile
from pathlib import Path

import kuzu
from loguru import logger as log

from shared.lakehouse import Lakehouse
from shared.settings import LOCAL_DIR, env


class GraphAnalytics:
    def __init__(self, schema: str):
        dbname = env.str(f"{schema.upper()}_GRAPH_DB")
        db_path = Path(LOCAL_DIR) / dbname

        if not db_path.exists():
            raise FileNotFoundError(f"db not found: {db_path}")

        db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(db)

        self.lh = Lakehouse()

    def compute_con_scores(
        self,
        node_label: str,
        rel_label: str,
        column_name: str = "con_score",
    ):
        log.info(
            "Computing CON scores for {} nodes via {} rels, storing to {} property",
            node_label,
            rel_label,
            column_name,
        )

        self.conn.execute(
            f"""
            ALTER TABLE {node_label}
            ADD IF NOT EXISTS {column_name} DOUBLE DEFAULT 0.0
            """
        )

        self.conn.execute(
            f"""
            MATCH (a:{node_label})-[ac:{rel_label}]->(c:{node_label})
            MATCH (b:{node_label})-[bc:{rel_label}]->(c:{node_label})
            WHERE a <> b
            WITH a, b,
                CASE
                    WHEN ac.esi < bc.esi
                    THEN ac.esi
                    ELSE bc.esi
                END AS min_esi
            WITH a, b, sum(min_esi) AS con_pair
            WITH a, sum(con_pair) AS con_score
            SET a["{column_name}"] = con_score
            """
        )
