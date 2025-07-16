WITH products AS (
    SELECT DISTINCT product_id
    FROM (
        SELECT product_id
        FROM {{ ref('edges_exports') }}

        UNION

        SELECT product_id
        FROM {{ ref('edges_imports') }}
    )
),
node_meta AS (
    SELECT max(node_id) + 1 AS start_node_id
    FROM {{ ref('nodes_countries') }}
)
SELECT
    node_meta.start_node_id + row_number() OVER () AS node_id,
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
    node_meta
WHERE
    product_id IN (SELECT product_id FROM products)
