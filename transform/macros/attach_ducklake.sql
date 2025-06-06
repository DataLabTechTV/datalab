{% macro attach_ducklake() %}

ATTACH 'ducklake:{{ env_var('LOCAL_DIR') }}/{{ env_var('STAGE_DB') }}' AS stage
(DATA_PATH 's3://{{ env_var('S3_BUCKET') }}/{{ env_var('S3_STAGE_PREFIX') }}');

{% endmacro %}
