import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Literal, Optional

import duckdb
import pandas as pd
from loguru import logger as log

from ml.types import InferenceResult
from shared.settings import LOCAL_DIR, env
from shared.storage import Storage, StoragePrefix
from shared.tools import generate_init_sql


class LakehouseException(Exception):
    pass


class Lakehouse:
    def __init__(self, read_only: bool = True):
        engine_db = os.path.join(LOCAL_DIR, env.str("ENGINE_DB"))

        log.info("Connecting to DuckDB: {}", engine_db)
        self.conn = duckdb.connect(engine_db, read_only=read_only)

        log.info("Initializing lakehouse with init SQL")

        try:
            init_sql = generate_init_sql()
            self.conn.execute(init_sql)
        except Exception as e:
            raise LakehouseException(f"Error executing init SQL: {e}")

        self.storage = Storage(prefix=StoragePrefix.EXPORTS)

    def export(self, catalog: str, schema: str) -> str:
        s3_export_path = self.storage.get_dir(f"{catalog}/{schema}", dated=True)

        log.info("Exporting {}.{} to {}", catalog, schema, s3_export_path)

        self.conn.execute(
            """
            SELECT
                table_catalog,
                table_schema,
                table_name
            FROM
                information_schema.tables
            WHERE
                table_catalog = ?
                AND table_schema = ?
            """,
            (catalog, schema),
        )

        tables = self.conn.fetchall()

        log.info(
            "Found {} tables in {}.{} for exporting",
            len(tables),
            catalog,
            schema,
        )

        for database, _, name in tables:
            if "nodes" in name:
                path = f"{s3_export_path}/nodes/{name}.parquet"
            elif "edges" in name:
                path = f"{s3_export_path}/edges/{name}.parquet"
            else:
                path = f"{s3_export_path}/{name}.parquet"

            table_fqn = f"{database}.{schema}.{name}"

            try:
                log.info("Exporting {} to {}", table_fqn, path)
                self.conn.execute(f"COPY {table_fqn} TO '{path}' (FORMAT parquet)")
            except:
                log.error(f"Could not export {table_fqn}: COPY failed")
                break

        self.storage.upload_manifest(f"{catalog}/{schema}", latest=s3_export_path)

        log.info("Export completed: {}", s3_export_path)

        return s3_export_path

    def latest_export(self, catalog: str, schema: str) -> Optional[str]:
        manifest = self.storage.load_manifest(f"{catalog}/{schema}")

        if manifest is None:
            return

        if "latest" not in manifest:
            log.warning("No latest field found in manifest")
            return

        return manifest["latest"]

    def load_into(self, catalog: str, schema: str, table_name: str, from_path: str):
        log.info("Loading into {}.{}.{}: {}", catalog, schema, table_name, from_path)

        suffix = Path(from_path).suffix.lstrip(".")

        if suffix not in ("parquet", "csv"):
            raise ValueError(f"file type not supported: {suffix}")

        self.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")

        self.conn.execute(
            f"""
            CREATE OR REPLACE TABLE {catalog}.{schema}.{table_name} AS
            SELECT * FROM '{from_path}'
            """
        )

    def load_docs_train_set(
        self,
        catalog: str,
        schema: str,
        table_name: str,
        k_folds: Literal[3, 5, 10] = 3,
    ) -> pd.DataFrame:
        log.info(
            "Loading train set from {}.{}.{} (k_folds={})",
            catalog,
            schema,
            table_name,
            k_folds,
        )

        match k_folds:
            case 3 | 5 | 10:
                folds_col = f"folds_{k_folds}_id"
            case _:
                raise ValueError(f"Unsupported number of folds: {k_folds}")

        rel = self.conn.sql(
            f"""--sql
            SELECT example_id, input, target, {folds_col} AS fold_id
            FROM "{catalog}"."{schema}"."{table_name}"
            WHERE NOT is_test
            """
        )

        return rel.to_df()

    def load_docs_test_set(
        self,
        catalog: str,
        schema: str,
        table_name: str,
    ) -> pd.DataFrame:
        log.info("Loading test set from {}.{}.{}", catalog, schema, table_name)

        rel = self.conn.sql(
            f"""--sql
            SELECT example_id, input, target
            FROM "{catalog}"."{schema}"."{table_name}"
            WHERE is_test
            """
        )

        return rel.to_df()

    def snapshot_id(self, catalog: str) -> int:
        log.info("Querying snapshot_id (version) for {} catalog", catalog)

        rel = self.conn.sql(
            f"""--sql
            SELECT max(snapshot_id) AS snapshot_id
            FROM "{catalog}".snapshots()
            """
        )

        snapshot_id = rel.to_df()["snapshot_id"].item()

        return snapshot_id

    def schema(
        self,
        catalog: str,
        schema: str,
        table_name: str,
    ) -> list[dict[str, str]]:
        log.info("Reading schema for {}.{}.{}", catalog, schema, table_name)

        self.conn.execute(
            f"""--sql
            SELECT *
            FROM "{catalog}"."{schema}"."{table_name}"
            LIMIT 0
            """
        )

        schema = [dict(name=desc[0], type=desc[1]) for desc in self.conn.description]

        return schema

    def count(
        self,
        catalog: str,
        schema: str,
        table_name: str,
        where: str | None = None,
    ) -> int:
        log.info("Counting rows in for {}.{}.{}", catalog, schema, table_name)

        query = f"""--sql
            SELECT count(*)
            FROM "{catalog}"."{schema}"."{table_name}"
        """

        if where is not None:
            query += f"""--sql
                WHERE {where}
            """

        self.conn.execute(query)

        count = self.conn.fetchone()[0]

        return count

    def log_inferences(self, schema: str, inference_results: list[InferenceResult]):
        log.info("Logging inference results (len={})", len(inference_results))

        self.conn.execute("INSTALL json")
        self.conn.execute("LOAD json")

        self.conn.execute(
            f"""--sql
            CREATE TABLE IF NOT EXISTS secure_stage."{schema}".inference_results (
                inference_uuid VARCHAR,
                model_name VARCHAR,
                model_version VARCHAR,
                dataset JSON,
                predictions UNION(
                    pred_bool BOOLEAN[],
                    pred_int INTEGER[],
                    pred_float FLOAT[]
                )
            )
            """
        )

        self.conn.execute(
            f"""--sql
            INSERT INTO secure_stage.{{schema}}.inference_results (
                inference_uuid,
                model_name,
                model_version,
                dataset,
                predictions
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                [
                    payload.inference_uuid,
                    payload.model_name,
                    payload.model_version,
                    json.dumps(asdict(payload.dataset)),
                    payload.predictions,
                ]
                for payload in inference_results
            ],
        )
