import os
from typing import Optional

from loguru import logger as log

from shared.settings import LOCAL_DIR, MART_SCHEMA_VARS, env
from shared.templates import (
    INIT_SQL_ATTACHED_DB_TPL,
    INIT_SQL_ATTACHED_SECURE_DB_TPL,
    INIT_SQL_TPL,
    reformat_render,
)


def generate_init_sql(path: Optional[str] = None) -> Optional[str]:
    log.info("Generating init SQL")

    log.info(
        "Found {} env vars for data mart DBs: {}",
        len(MART_SCHEMA_VARS),
        ", ".join(MART_SCHEMA_VARS),
    )

    schema_vars = [
        "PSQL_CATALOG_STAGE_SCHEMA",
        "PSQL_CATALOG_SECURE_STAGE_SCHEMA",
    ] + MART_SCHEMA_VARS

    attachments_sql = []

    for varname in schema_vars:
        basename = varname.removeprefix("PSQL_CATALOG_").removesuffix("_SCHEMA")
        s3_prefix = env.str(f"S3_{basename}_PREFIX")

        match varname:
            case "PSQL_CATALOG_SECURE_STAGE_SCHEMA":
                tpl = INIT_SQL_ATTACHED_SECURE_DB_TPL
            case _:
                tpl = INIT_SQL_ATTACHED_DB_TPL

        attachment_sql = reformat_render(
            tpl.substitute(
                s3_bucket=env.str("S3_BUCKET"),
                s3_prefix=s3_prefix,
                psql_schema=env.str(varname),
            )
        )

        attachments_sql.append(attachment_sql)

    init_sql = reformat_render(
        INIT_SQL_TPL.substitute(
            s3_access_key_id=env.str("S3_ACCESS_KEY_ID"),
            s3_secret_access_key=env.str("S3_SECRET_ACCESS_KEY"),
            s3_endpoint=env.str("S3_ENDPOINT"),
            s3_use_ssl=env.str("S3_USE_SSL"),
            s3_url_style=env.str("S3_URL_STYLE"),
            s3_region=env.str("S3_REGION"),
            psql_host=env.str("PSQL_CATALOG_HOST"),
            psql_port=env.str("PSQL_CATALOG_PORT"),
            psql_db=env.str("PSQL_CATALOG_DB"),
            psql_user=env.str("PSQL_CATALOG_USER"),
            psql_password=env.str("PSQL_CATALOG_PASSWORD"),
        )
    )

    if path is None:
        return f"{init_sql}\n{'\n'.join(attachments_sql)}".strip()

    with open(path, "w") as fp:
        fp.write(init_sql)
        fp.write("\n")
        fp.write("\n".join(attachments_sql))

    log.info("File written: {}", path)
