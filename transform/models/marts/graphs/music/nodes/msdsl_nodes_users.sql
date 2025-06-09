SELECT DISTINCT
    'm_' || user_id AS node_id,
    user_id,
    'MSDSL' AS source
FROM {{ ref('msdsl_user_listening_history') }}
ORDER BY user_id
