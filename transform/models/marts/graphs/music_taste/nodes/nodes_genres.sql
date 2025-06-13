WITH all_genres AS (
    SELECT unnest(genres) AS genre
    FROM {{ ref('dsn_hr_genres') }}

    UNION

    SELECT unnest(genres) AS genre
    FROM {{ ref('dsn_hu_genres') }}

    UNION

    SELECT unnest(genres) AS genre
    FROM {{ ref('dsn_ro_genres') }}

    UNION

    SELECT unnest(tags) AS genre
    FROM {{ ref('msdsl_music_info') }}
)
SELECT DISTINCT
    genre AS node_id,
    genre
FROM all_genres
ORDER BY genre
