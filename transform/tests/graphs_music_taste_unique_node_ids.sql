WITH all_ids AS (
    SELECT node_id
    FROM {{ ref('dsn_nodes_users') }}

    UNION

    SELECT node_id
    FROM {{ ref('msdsl_nodes_tracks') }}

    UNION

    SELECT node_id
    FROM {{ ref('msdsl_nodes_users') }}

    UNION

    SELECT node_id
    FROM {{ ref('nodes_genres') }}
),
duplicate_ids AS (
    SELECT node_id
    FROM all_ids
    GROUP BY node_id
    HAVING COUNT(*) > 1
)
SELECT *
FROM duplicate_ids
