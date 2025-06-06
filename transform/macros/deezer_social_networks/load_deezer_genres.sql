{% macro load_deezer_genres(s3_path) %}

WITH raw_json AS (
    SELECT *
    FROM read_json_auto('{{ s3_path }}')
    LIMIT 10
),
users AS (
  SELECT unnest(json_keys(json)) AS user_id
  FROM raw_json
)
SELECT user_id
FROM users
-- SELECT j.key AS user_id, j.value AS genres
-- FROM raw_json, json_each(raw_json.json) AS j

{% endmacro %}
