SELECT
    track_id,
    name,
    artist,
    year
FROM {{ ref('msdsl_music_info') }}
