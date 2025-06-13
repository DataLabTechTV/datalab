WITH track_genres AS (
    SELECT track_id, unnest(tags) AS genre
    FROM {{ ref('msdsl_music_info') }}
)
SELECT sn.node_id AS source_id, tn.node_id AS target_id
FROM track_genres tg

JOIN {{ ref('msdsl_nodes_tracks') }} AS sn
ON tg.track_id = sn.track_id

JOIN {{ ref('nodes_genres') }} AS tn
ON tg.genre = tn.genre
