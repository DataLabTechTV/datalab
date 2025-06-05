{{ config(materialized='table') }}

select *
from read_json_auto('s3://lakehouse/raw/deezer_social_networks/2025_06_04/16_44_30_382/RO/RO_genres.json')
