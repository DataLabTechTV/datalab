{{ config(alias='dataset') }}

WITH dataset AS (
    SELECT
        row_number() OVER () AS doc_id,
        clean_text AS text,
        (is_depression = 1) AS label,
        row_number() OVER (PARTITION BY is_depression ORDER BY clean_text) AS rn,
        count(*) OVER (PARTITION BY is_depression) AS cnt
    FROM read_csv(
        '{{ env_var("RAW__DEPRESSION_DETECTION__DEPRESSION_DATASET_REDDIT_TWITTER") }}',
        delim = ',',
        quote = '"',
        escape = '"',
        header = true,
        columns = {
            clean_text: VARCHAR,
            is_depression: BOOLEAN
        }
    )
)
SELECT
    text,
    label,
    (rn <= cnt * 0.2) AS is_test,
    CASE
        WHEN rn < cnt * 0.2 THEN 0
        WHEN rn >= cnt * 0.2 AND rn < cnt * 0.4 THEN 1
        WHEN rn >= cnt * 0.4 AND rn < cnt * 0.6 THEN 2
        WHEN rn >= cnt * 0.6 AND rn < cnt * 0.8 THEN 3
        ELSE 4
    END AS "folds_5_id",
    CASE
        WHEN rn < cnt * 0.1 THEN 0
        WHEN rn >= cnt * 0.1 AND rn < cnt * 0.2 THEN 1
        WHEN rn >= cnt * 0.2 AND rn < cnt * 0.3 THEN 2
        WHEN rn >= cnt * 0.3 AND rn < cnt * 0.4 THEN 3
        WHEN rn >= cnt * 0.4 AND rn < cnt * 0.5 THEN 4
        WHEN rn >= cnt * 0.5 AND rn < cnt * 0.6 THEN 5
        WHEN rn >= cnt * 0.6 AND rn < cnt * 0.7 THEN 6
        WHEN rn >= cnt * 0.7 AND rn < cnt * 0.8 THEN 7
        WHEN rn >= cnt * 0.8 AND rn < cnt * 0.9 THEN 8
        ELSE 9
    END AS "folds_10_id"
FROM
    dataset
ORDER BY
    doc_id
