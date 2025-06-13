SELECT
    sn.node_id AS source_id,
    tn.node_id AS target_id,
    play_count
FROM {{ ref('msdsl_user_listening_history') }} uh

JOIN {{ ref('msdsl_nodes_users') }} AS sn
ON uh.user_id = sn.user_id

JOIN {{ ref('msdsl_nodes_tracks') }} AS tn
ON uh.track_id = tn.track_id
