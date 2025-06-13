WITH n AS (
    SELECT max(node_id) AS start_node_id
    FROM {{ ref('dsn_nodes_users') }}
)
SELECT
    n.start_node_id + row_number() OVER () AS node_id,
    track_id,
    name,
    artist,
    year
FROM {{ ref('msdsl_music_info') }}, n
