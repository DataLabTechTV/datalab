{{ config(alias='cc_metrics') }}

WITH country_exports AS (
    SELECT
        country_id,
        country_iso3_code,
        product_id,
        product_hs92_code,
        sum(export_value) AS export_value
    FROM
        {{ ref('taoec_hs92_ccp_trade_3y_latest') }}
    GROUP BY
        country_id,
        country_iso3_code,
        product_id,
        product_hs92_code
),
shares AS (
    SELECT
        country_id,
        country_iso3_code,
        product_id,
        product_hs92_code,
        export_value / sum(export_value) OVER (PARTITION BY country_id) AS share
    FROM country_exports
)
SELECT
    a.country_id AS country_id_1,
    a.country_iso3_code AS country_iso3_code_1,
    b.country_id AS country_id_2,
    b.country_iso3_code AS country_iso3_code_2,
    sum(least(a.share, b.share)) AS esi
FROM shares a
JOIN shares b
ON a.product_id = b.product_id
WHERE a.country_id <> b.country_id
GROUP BY
    a.country_id,
    a.country_iso3_code,
    b.country_id,
    b.country_iso3_code
