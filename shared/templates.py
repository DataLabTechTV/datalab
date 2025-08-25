import textwrap
from string import Template

INIT_SQL_ATTACHED_DB_TPL = Template(
    """--sql
    ATTACH IF NOT EXISTS 'ducklake:sqlite:$db_path'
    (DATA_PATH 's3://$s3_bucket/$s3_prefix');
    """
)

INIT_SQL_ATTACHED_SECURE_DB_TPL = Template(
    """--sql
    ATTACH IF NOT EXISTS 'ducklake:sqlite:$db_path'
    (DATA_PATH 's3://$s3_bucket/$s3_prefix', ENCRYPTED 1);
    """
)

INIT_SQL_TPL = Template(
    """--sql
    -- Your .env config should be reproduced below.

    -- Use this to access your DuckLake manually from the CLI:
    -- $$ duckdb -init local/init.sql local/engine.duckdb

    INSTALL httpfs;
    INSTALL parquet;
    INSTALL sqlite;
    INSTALL ducklake;

    CREATE OR REPLACE SECRET minio (
        TYPE s3,
        PROVIDER config,
        KEY_ID '$s3_access_key_id',
        SECRET '$s3_secret_access_key',
        ENDPOINT '$s3_endpoint',
        USE_SSL $s3_use_ssl,
        URL_STYLE '$s3_url_style',
        REGION '$s3_region'
    );
    """
)


def reformat_render(template: str):
    return textwrap.dedent(template.replace("--sql\n", ""))
