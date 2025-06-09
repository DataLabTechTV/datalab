{{ config(alias='hr_genres') }}

{{ load_deezer_genres(env_var("RAW__DEEZER_SOCIAL_NETWORKS__HR__HR_GENRES")) }}
