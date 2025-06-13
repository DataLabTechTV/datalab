WITH all_users AS (
    SELECT
        g.user_id AS user_id,
        'HR' AS country
    FROM {{ ref('dsn_hr_genres') }} AS g

    UNION

    SELECT
        g.user_id AS user_id,
        'HU' AS country
    FROM {{ ref('dsn_hu_genres') }} AS g

    UNION

    SELECT
        g.user_id AS user_id,
        'RO' AS country
    FROM {{ ref('dsn_ro_genres') }} AS g
)
SELECT
    row_number() OVER () AS node_id,
    user_id,
    country,
    'Deezer' AS source
FROM all_users
