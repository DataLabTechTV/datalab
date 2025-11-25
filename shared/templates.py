import textwrap
from string import Template

INIT_SQL_ATTACHED_DB_TPL = Template(
    """--sql
    ATTACH 'ducklake:' AS $psql_schema (
        METADATA_SCHEMA '$psql_schema',
        DATA_PATH 's3://$s3_bucket/$s3_prefix'
    );
    """
)

INIT_SQL_ATTACHED_SECURE_DB_TPL = Template(
    """--sql
    ATTACH 'ducklake:' AS $psql_schema (
        METADATA_SCHEMA '$psql_schema',
        DATA_PATH 's3://$s3_bucket/$s3_prefix',
        ENCRYPTED 1
    );
    """
)

INIT_SQL_TPL = Template(
    """--sql
    -- Your .env config should be reproduced below.

    -- Use this to access your DuckLake manually from the CLI:
    -- $$ duckdb -init local/init.sql local/engine.duckdb

    INSTALL httpfs;
    INSTALL parquet;
    INSTALL postgres;
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

    CREATE OR REPLACE SECRET postgres (
        TYPE postgres,
        HOST '$psql_host',
        PORT $psql_port,
        DATABASE $psql_db,
        USER '$psql_user',
        PASSWORD '$psql_password'
    );

    CREATE OR REPLACE SECRET (
        TYPE ducklake,
        METADATA_PATH '',
        METADATA_PARAMETERS MAP {
            'TYPE': 'postgres',
            'SECRET': 'postgres'
        }
    );
    """
)


def reformat_render(template: str):
    return textwrap.dedent(template.replace("--sql\n", ""))
