{{ config(alias='competing_countries_products', materialized='view') }}

SELECT DISTINCT
    product_id
FROM
    {{ ref('taoec_hs92_ccp_trade_3y_latest') }}
WHERE
    country_id IN (
        SELECT country_id
        FROM {{ ref('taoec_competing_countries') }}
    )
    OR partner_country_id IN (
        SELECT country_id
        FROM {{ ref('taoec_competing_countries') }}
    )
