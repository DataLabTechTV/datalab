SELECT
    'm_' || user_id AS source_id,
    track_id AS target_id,
    play_count
FROM {{ ref('msdsl_user_listening_history') }}
