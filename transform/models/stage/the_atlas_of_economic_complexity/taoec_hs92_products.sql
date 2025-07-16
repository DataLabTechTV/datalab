{{ config(alias='hs92_products') }}

SELECT
    product_id,
    product_hs92_code,
    product_level,
    product_name,
    product_name_short,
    product_parent_id,
    product_id_hierarchy,
    show_feasibility,
    natural_resource,
    green_product
FROM read_csv(
    '{{ env_var("RAW__THE_ATLAS_OF_ECONOMIC_COMPLEXITY__CLASSIFICATIONS__PRODUCT_HS92") }}',
    delim = ',',
    quote = '"',
    escape = '"',
    header = true,
    nullstr = ['XXXX', 'XXXXXX', '', '9999AA'],
    columns = {
        product_id: USMALLINT,
        product_hs92_code: UINTEGER,
        product_level: UTINYINT,
        product_name: VARCHAR,
        product_name_short: VARCHAR,
        product_parent_id: USMALLINT,
        product_id_hierarchy: VARCHAR,
        show_feasibility: BOOLEAN,
        natural_resource: BOOLEAN,
        green_product: BOOLEAN
    }
)
