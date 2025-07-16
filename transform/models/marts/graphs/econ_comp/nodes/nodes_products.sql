WITH node_meta AS (
    SELECT max(node_id) + 1 AS start_node_id
    FROM {{ ref('nodes_countries') }}
)
SELECT
    n.start_node_id + row_number() OVER () AS node_id,
    product_id,
    product_hs92_code,
    product_level,
    product_name,
    product_name_short,
    product_id_hierarchy,
    show_feasibility,
    natural_resource,
    green_product
FROM
    {{ ref('taoec_hs92_products') }},
    node_meta AS n
WHERE
    product_id IN (
        SELECT product_id
        FROM {{ ref('taoec_competing_countries_products') }}
    )
