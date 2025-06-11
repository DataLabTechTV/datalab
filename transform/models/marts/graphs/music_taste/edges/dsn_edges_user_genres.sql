SELECT
    'd_hr_' || user_id AS source_id,
    unnest(genres) AS target_id
FROM {{ ref('dsn_hr_genres' )}}

UNION

SELECT
    'd_hu_' || user_id AS source_id,
    unnest(genres) AS target_id
FROM {{ ref('dsn_hu_genres' )}}

UNION

SELECT
    'd_hu_' || user_id AS source_id,
    unnest(genres) AS target_id
FROM {{ ref('dsn_ro_genres' )}}
