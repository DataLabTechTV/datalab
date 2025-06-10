import os

import duckdb
from loguru import logger as log

from shared.settings import LOCAL_DIR, env


class LakehouseException(Exception):
    pass


class Lakehouse:
    def __init__(self, read_only: bool = True, init_sql_path: str = "scripts/init.sql"):
        engine_db = os.path.join(LOCAL_DIR, env.str("ENGINE_DB"))

        log.info("Connecting to DuckDB: {}", engine_db)
        self.con = duckdb.connect(engine_db, read_only=read_only)

        log.info("Initializing lakehouse with SQL script: {}", init_sql_path)

        if not os.path.exists(init_sql_path):
            raise LakehouseException(f"Init SQL script not found: {init_sql_path}")

        try:
            with open(init_sql_path) as fp:
                self.con.execute(fp.read())
        except:
            raise LakehouseException(
                f"Error executing init SQL script: {init_sql_path}"
            )

        self.stage_catalog = os.path.splitext(env.str("STAGE_DB"))[0]
        self.marts_catalog = os.path.splitext(env.str("MARTS_DB"))[0]

        log.info("Attaching {} DuckLake catalog", self.stage_catalog)

        self.con.execute(
            f"""
            ATTACH IF NOT EXISTS 'ducklake:sqlite:{LOCAL_DIR}/{env.str('STAGE_DB')}'
            (DATA_PATH 's3://{env.str('S3_BUCKET') }/{env.str('S3_STAGE_PREFIX')}')
            """
        )

        log.info("Attaching {} DuckLake catalog", self.marts_catalog)

        self.con.execute(
            f"""
            ATTACH IF NOT EXISTS 'ducklake:sqlite:{LOCAL_DIR}/{env.str('MARTS_DB')}'
            (DATA_PATH 's3://{env.str('S3_BUCKET') }/{env.str('S3_MARTS_PREFIX')}')
            """
        )

        self.s3_exports_path = (
            f"s3://{env.str('S3_BUCKET')}/{env.str('S3_EXPORTS_PREFIX')}"
        )

    def export(self, schema: str) -> str:
        log.info(
            "Exporting {}.{} to {}",
            self.marts_catalog,
            schema,
            f"{self.s3_exports_path}/{schema}",
        )

        self.con.execute(
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
            (
                self.marts_catalog,
                schema,
            ),
        )

        tables = self.con.fetchall()

        log.info(
            "Found {} tables in {}.{} for exporting",
            len(tables),
            self.marts_catalog,
            schema,
        )

        s3_export_path = f"{self.s3_exports_path}/{schema}"

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
                self.con.execute(f"COPY {table_fqn} TO '{path}' (FORMAT parquet)")
            except:
                log.error(f"Could not export {table_fqn}: COPY failed")
                break

        log.info("Export completed: {}", s3_export_path)

        return s3_export_path
