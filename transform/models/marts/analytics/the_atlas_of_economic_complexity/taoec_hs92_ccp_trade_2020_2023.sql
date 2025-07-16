{{ config(alias='hs92_ccp_trade_2020_2023', materialized='view') }}

SELECT
    country_id,
    country_iso3_code,
    partner_country_id,
    partner_iso3_code,
    product_id,
    product_hs92_code,
    sum(export_value) AS export_value,
    sum(import_value) AS import_value
FROM {{ ref('taoec_hs92_ccp_trade') }}
GROUP BY
    country_id,
    country_iso3_code,
    partner_country_id,
    partner_iso3_code,
    product_id,
    product_hs92_code
