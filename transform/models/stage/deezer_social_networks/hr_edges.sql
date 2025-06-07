{{ config(materialized='table') }}

{{ load_deezer_edges(env_var("RAW__DEEZER_SOCIAL_NETWORKS__HR__HR_EDGES")) }}
