{% macro load_deezer_edges(s3_path) %}

SELECT
    node_1 AS source,
    node_2 AS target
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
