SELECT
    'd_' || user_id AS source_id,
    unnest(genres) AS target_id
FROM {{ ref('dsn_hr_genres' )}}

UNION

SELECT
    'd_' || user_id AS source_id,
    unnest(genres) AS target_id
FROM {{ ref('dsn_hu_genres' )}}

UNION

SELECT
    'd_' || user_id AS source_id,
    unnest(genres) AS target_id
FROM {{ ref('dsn_ro_genres' )}}
