SELECT product_id, product_parent_id
FROM {{ ref('taoec_hs92_products') }}
