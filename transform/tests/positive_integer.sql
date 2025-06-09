SELECT *
FROM {{ model }}
WHERE {{ column }} IS NULL
    OR {{ column }} <= 0
    OR CAST({{ column_name }} AS TEXT) !~ '^\d+$'
