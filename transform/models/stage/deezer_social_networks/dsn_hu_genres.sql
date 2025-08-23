{{ config(alias='hu_genres') }}

{{ load_deezer_genres(env_var("RAW__DEEZER_SOCIAL_NETWORKS__HU__HU_GENRES", "NOT_FOUND")) }}
