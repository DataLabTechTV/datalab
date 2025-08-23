{{ config(alias='ro_genres') }}

{{ load_deezer_genres(env_var("RAW__DEEZER_SOCIAL_NETWORKS__RO__RO_GENRES", "NOT_FOUND")) }}
