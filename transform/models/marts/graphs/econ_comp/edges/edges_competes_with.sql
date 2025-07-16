SELECT country_id_1, country_id_2, esi
FROM {{ ref('taoec_cc_metrics') }}
ORDER BY esi DESC
LIMIT 5%
