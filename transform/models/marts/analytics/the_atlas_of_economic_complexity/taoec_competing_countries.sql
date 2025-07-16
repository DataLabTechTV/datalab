{{ config(alias='competing_countries', materialized='view') }}

WITH countries AS (
    SELECT country_id_1, country_id_2
    FROM {{ ref('taoec_cc_metrics') }}
    ORDER BY esi DESC
    LIMIT 5%
)
SELECT country_id_1 AS country_id
FROM countries

UNION

SELECT country_id_2 AS country_id
FROM countries
