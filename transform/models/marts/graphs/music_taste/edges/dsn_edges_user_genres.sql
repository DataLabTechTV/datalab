WITH user_genres AS (
    SELECT
        user_id,
        unnest(genres) AS genre,
        'HR' AS country
    FROM {{ ref('dsn_hr_genres' )}}

    UNION

    SELECT
        user_id,
        unnest(genres) AS genre,
        'HU' AS country
    FROM {{ ref('dsn_hu_genres' )}}

    UNIOn

    SELECT
        user_id,
        unnest(genres) AS genre,
        'RO' AS country
    FROM {{ ref('dsn_ro_genres' )}}
)

SELECT sn.node_id AS source_id, tn.node_id AS target_id
FROM user_genres ug

JOIN {{ ref('dsn_nodes_users') }} AS sn
ON ug.user_id = sn.user_id AND sn.country = ug.country

JOIN {{ ref('nodes_genres') }} AS tn
ON ug.genre = tn.genre
