SELECT
    row_number() OVER () AS node_id,
    country_id,
    country_iso3_code,
    country_name,
    country_name_short,
    in_rankings,
    former_country
FROM
    {{ ref('taoec_countries') }}
WHERE
    country_id IN (
        SELECT country_id
        FROM {{ ref('taoec_competing_countries') }}
    )
