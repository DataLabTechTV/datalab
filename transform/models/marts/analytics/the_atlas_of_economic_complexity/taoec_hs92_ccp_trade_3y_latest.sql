{{ config(alias='hs92_ccp_trade_3y_latest', materialized='view') }}

SELECT
    country_id,
    country_iso3_code,
    partner_country_id,
    partner_iso3_code,
    product_id,
    product_hs92_code,
    min(year) AS since_year,
    max(year) AS until_year,
    sum(export_value) AS export_value,
    sum(import_value) AS import_value
FROM {{ ref('taoec_hs92_ccp_trade') }}
WHERE year >= (
    SELECT max(year) - 3
    FROM {{ ref('taoec_hs92_ccp_trade') }}
)
GROUP BY
    country_id,
    country_iso3_code,
    partner_country_id,
    partner_iso3_code,
    product_id,
    product_hs92_code
