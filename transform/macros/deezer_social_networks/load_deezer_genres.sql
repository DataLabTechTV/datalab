{% macro load_deezer_genres(s3_path) %}

WITH user_genres AS (
    UNPIVOT (
        FROM read_json(
            '{{ s3_path }}',
            records=true,
            map_inference_threshold=-1
        )
    )
    ON *
    INTO
        NAME user_id
        VALUE genres
)
SELECT CAST(user_id AS iNTEGER) AS user_id, genres
from user_genres

{% endmacro %}
