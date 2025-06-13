WITH all_users AS (
    SELECT DISTINCT user_id
    FROM {{ ref('msdsl_user_listening_history') }}
),
n AS (
    SELECT max(node_id) + 1 AS start_node_id
    FROM {{ ref('msdsl_nodes_tracks') }}
)
SELECT DISTINCT
    n.start_node_id + row_number() OVER () AS node_id,
    user_id,
    'MSDSL' AS source
FROM all_users, n
