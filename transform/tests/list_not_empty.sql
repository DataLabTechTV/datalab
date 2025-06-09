SELECT *
FROM {{ model }}
WHERE {{ columns }} IS NULL
    OR len({{ column }}) = 0
