{% macro load_deezer_genres(s3_path) %}

WITH raw_json AS (
    SELECT *
    FROM read_json_auto('{{ s3_path }}')
)
SELECT CAST(je.key AS INTEGER) AS user_id, CAST(je.value AS VARCHAR[]) AS genres
FROM raw_json rj, json_each(rj.json) AS je

{% endmacro %}
