SELECT
    track_id AS source_id,
    unnest(tags) AS target_id
FROM {{ ref('msdsl_music_info') }}
