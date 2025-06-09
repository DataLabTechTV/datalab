{{ config(name='user_listening_history') }}

SELECT
    track_id,
    user_id,
    playcount AS play_count
FROM read_csv(
    '{{ env_var("RAW__MILLION_SONG_DATASET_SPOTIFY_LASTFM__USER_LISTENING_HISTORY") }}',
    delim = ',',
    header = true,
    columns = {
        track_id: VARCHAR,
        user_id: VARCHAR,
        playcount: INTEGER
    }
)
