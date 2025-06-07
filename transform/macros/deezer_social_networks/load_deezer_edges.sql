{% macro load_deezer_edges(s3_path) %}

SELECT
    CAST(node_1 AS INTEGER) AS source_id,
    CAST(node_2 AS INTEGER) AS target_id
FROM read_csv(
    '{{ s3_path }}',
    delim = ',',
    header = true,
    columns = {
        node_1: VARCHAR,
        node_2: VARCHAR
    }
)

{% endmacro %}
