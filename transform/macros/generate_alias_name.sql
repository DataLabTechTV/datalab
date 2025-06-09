{% macro generate_alias_name(custom_alias_name=none, node=none) %}
  {{ return(custom_alias_name or node.name) }}
{% endmacro %}
