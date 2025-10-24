ALTER TABLE ducklake_snapshot
    ALTER COLUMN snapshot_time
        TYPE TIMESTAMPTZ
        USING snapshot_time::TIMESTAMPTZ;

ALTER TABLE ducklake_schema
    ALTER COLUMN schema_uuid
        TYPE UUID
        USING schema_uuid::UUID,
    ALTER COLUMN path_is_relative
        TYPE BOOLEAN
        USING path_is_relative::INTEGER = 1;

ALTER TABLE ducklake_table
    ALTER COLUMN table_uuid
        TYPE UUID
        USING table_uuid::UUID,
    ALTER COLUMN path_is_relative
        TYPE BOOLEAN
        USING path_is_relative::INTEGER = 1;

ALTER TABLE ducklake_view
    ALTER COLUMN view_uuid
        TYPE UUID
        USING view_uuid::UUID;

ALTER TABLE ducklake_data_file
    ALTER COLUMN path_is_relative
        TYPE BOOLEAN
        USING path_is_relative::INTEGER = 1;

ALTER TABLE ducklake_file_column_stats
    ALTER COLUMN contains_nan
        TYPE BOOLEAN
        USING contains_nan::INTEGER = 1;

ALTER TABLE ducklake_delete_file
    ALTER COLUMN path_is_relative
        TYPE BOOLEAN
        USING path_is_relative::INTEGER = 1;

ALTER TABLE ducklake_column
    ALTER COLUMN nulls_allowed
        TYPE BOOLEAN
        USING nulls_allowed::INTEGER = 1;

ALTER TABLE ducklake_table_column_stats
    ALTER COLUMN contains_null
        TYPE BOOLEAN
        USING contains_null::INTEGER = 1,
    ALTER COLUMN contains_nan
        TYPE BOOLEAN
        USING contains_nan::INTEGER = 1;

ALTER TABLE ducklake_files_scheduled_for_deletion
    ALTER COLUMN path_is_relative
        TYPE BOOLEAN
        USING path_is_relative::INTEGER = 1,
    ALTER COLUMN schedule_start
        TYPE TIMESTAMPTZ
        USING schedule_start::TIMESTAMPTZ;

ALTER TABLE ducklake_name_mapping
    ALTER COLUMN is_partition
        TYPE BOOLEAN
        USING is_partition::INTEGER = 1;
