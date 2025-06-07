SELECT
    'd_' || g.user_id AS node_id,
    g.user_id AS user_id,
    'Deezer' AS source,
    'HR' AS country
FROM {{ ref('hr_genres') }} AS g

UNION

SELECT
    'd_' || g.user_id AS node_id,
    g.user_id AS user_id,
    'Deezer' AS source,
    'HU' AS country
FROM {{ ref('hu_genres') }} AS g

UNION

SELECT
    'd_' || g.user_id AS node_id,
    g.user_id AS user_id,
    'Deezer' AS source,
    'RO' AS country
FROM {{ ref('ro_genres') }} AS g

ORDER BY g.user_id
