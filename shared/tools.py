import os
from typing import Optional

from loguru import logger as log

from shared.settings import LOCAL_DIR, MART_DB_VARS, env
from shared.templates import INIT_SQL_ATTACHED_DB_TPL, INIT_SQL_TPL, reformat_render


def generate_init_sql(path: Optional[str] = None) -> Optional[str]:
    log.info("Generating init SQL")

    log.info(
        "Found {} env vars for data mart DBs: {}",
        len(MART_DB_VARS),
        ", ".join(MART_DB_VARS),
    )

    attachments_sql = []

    for varname in ["STAGE_DB"] + MART_DB_VARS:
        if varname == "STAGE_DB":
            s3_prefix = env.str("S3_STAGE_PREFIX")
        else:
            s3_prefix = env.str(f"S3_{varname.strip('_DB')}_PREFIX")

        attachment_sql = reformat_render(
            INIT_SQL_ATTACHED_DB_TPL.substitute(
                db_path=os.path.join(LOCAL_DIR, env.str(varname)),
                s3_bucket=env.str("S3_BUCKET"),
                s3_prefix=s3_prefix,
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
        )
    )

    if path is None:
        return f"{init_sql}\n{'\n'.join(attachments_sql)}".strip()

    with open(path, "w") as fp:
        fp.write(init_sql)
        fp.write("\n")
        fp.write("\n".join(attachments_sql))

    log.info("File written: {}", path)
