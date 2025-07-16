{{ config(alias='countries') }}

SELECT
    country_id,
    country_iso3_code,
    country_name,
    country_name_short,
    in_rankings,
    former_country
FROM read_csv(
    '{{ env_var("RAW__THE_ATLAS_OF_ECONOMIC_COMPLEXITY__CLASSIFICATIONS__LOCATION_COUNTRY") }}',
    delim = ',',
    quote = '"',
    escape = '"',
    header = true,
    columns = {
        country_id: USMALLINT,
        country_iso3_code: VARCHAR,
        country_name: VARCHAR,
        country_name_short: VARCHAR,
        in_rankings: BOOLEAN,
        former_country: BOOLEAN
    }
)
