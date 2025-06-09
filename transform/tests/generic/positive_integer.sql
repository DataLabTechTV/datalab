{% test positive_integer(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NULL
    OR {{ column_name }} <= 0
    OR CAST({{ column_name }} AS TEXT) !~ '^\d+$'

{% endtest %}
