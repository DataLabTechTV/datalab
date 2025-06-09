{% test list_not_empty(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NULL
    OR len({{ column_name }}) = 0

{% endtest %}
