WITH all_genres AS (
    SELECT unnest(genres) AS genre
    FROM {{ ref('dsn_hr_genres') }}

    UNION

    SELECT unnest(genres) AS genre
    FROM {{ ref('dsn_hu_genres') }}

    UNION

    SELECT unnest(genres) AS genre
    FROM {{ ref('dsn_ro_genres') }}
)
SELECT DISTINCT genre
FROM all_genres
ORDER BY genre
