SELECT *
FROM {{ ref('taoec_cc_metrics') }}
WHERE esi < 0 OR esi > 1
