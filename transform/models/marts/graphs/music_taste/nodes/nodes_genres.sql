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
),
unique_genres AS (
    SELECT DISTINCT genre
    FROM all_genres
),
n AS (
    SELECT max(node_id) + 1 AS start_node_id
    FROM {{ ref('msdsl_nodes_users') }}
)
SELECT
    n.start_node_id + row_number() OVER () AS node_id,
    genre
FROM unique_genres, n
