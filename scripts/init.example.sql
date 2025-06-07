-- Use this to access your DuckLake manually from the CLI:
-- $ duckdb -init scripts/init.sql local/engine.duckdb

-- Reproduce your .env config below.
-- Make sure to update the stage and marts paths, if you changed them.

INSTALL httpfs;
INSTALL parquet;
INSTALL sqlite;
INSTALL ducklake;

CREATE OR REPLACE SECRET minio (
    TYPE s3,
    PROVIDER config,
    KEY_ID 'minio_username',
    SECRET 'minio_password',
    ENDPOINT 'localhost:9000',
    USE_SSL false,
    URL_STYLE 'path',
    REGION 'eu-west-1'
);

ATTACH 'ducklake:sqlite:./local/stage.sqlite' (DATA_PATH 's3://lakehouse/stage');

ATTACH 'ducklake:sqlite:./local/marts.sqlite' (DATA_PATH 's3://lakehouse/marts');
