{% macro generate_schema_name(custom_schema_name, node) %}
  {{ return(custom_schema_name or target.schema) }}
{% endmacro %}
