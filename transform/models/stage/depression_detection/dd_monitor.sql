{{ config(alias='monitor') }}

SELECT
    row_number() OVER () AS example_id,
    text AS input,
    CAST(label AS DOUBLE) AS target
FROM read_csv(
    '{{ env_var("RAW__DEPRESSION__CLEAN_ENCODED_DF") }}',
    delim = ',',
    header = true,
    columns = {
        text: VARCHAR,
        label: USMALLINT
    }
)
