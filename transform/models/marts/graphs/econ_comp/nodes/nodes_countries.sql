WITH countries AS (
    SELECT DISTINCT country_id
    FROM (
        SELECT country_id_1 AS country_id
        FROM {{ ref('edges_competes_with') }}

        UNION

        SELECT country_id_2 AS country_id
        FROM {{ ref('edges_competes_with') }}
    )
)
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
    country_id IN (SELECT country_id FROM countries)
