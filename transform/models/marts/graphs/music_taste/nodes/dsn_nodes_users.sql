SELECT
    'd_hr_' || g.user_id AS node_id,
    g.user_id AS user_id,
    'Deezer' AS source,
    'HR' AS country
FROM {{ ref('dsn_hr_genres') }} AS g

UNION

SELECT
    'd_hu_' || g.user_id AS node_id,
    g.user_id AS user_id,
    'Deezer' AS source,
    'HU' AS country
FROM {{ ref('dsn_hu_genres') }} AS g

UNION

SELECT
    'd_ro_' || g.user_id AS node_id,
    g.user_id AS user_id,
    'Deezer' AS source,
    'RO' AS country
FROM {{ ref('dsn_ro_genres') }} AS g

ORDER BY g.user_id
