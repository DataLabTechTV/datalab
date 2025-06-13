SELECT
    track_id AS node_id,
    track_id,
    name,
    artist,
    year
FROM {{ ref('msdsl_music_info') }}
