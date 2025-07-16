{{ config(alias='hs92_ccp_trade') }}

SELECT
    country_id,
    country_iso3_code,
    partner_country_id,
    partner_iso3_code,
    product_id,
    product_hs92_code,
    year,
    export_value,
    import_value
FROM read_csv(
    '{{ env_var("RAW__THE_ATLAS_OF_ECONOMIC_COMPLEXITY__HS92__HS92_COUNTRY_COUNTRY_PRODUCT_YEAR_6_2020_2023") }}',
    delim = ',',
    quote = '"',
    escape = '"',
    header = true,
    nullstr = ['XXXXXX'],
    columns = {
        country_id: USMALLINT,
        country_iso3_code: VARCHAR,
        partner_country_id: USMALLINT,
        partner_iso3_code: VARCHAR,
        product_id: USMALLINT,
        product_hs92_code: UINTEGER,
        year: USMALLINT,
        export_value: BIGINT,
        import_value: BIGINT
    }
)
