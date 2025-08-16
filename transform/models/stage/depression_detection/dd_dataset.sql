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
),
train_test_split AS (
    SELECT doc_id, text, label, (rn <= cnt * 0.2) AS is_test
    FROM dataset
),
train_set AS (
    SELECT
        doc_id,
        text,
        label,
        is_test,
        row_number() OVER (PARTITION BY label ORDER BY text) AS rn,
        count(*) OVER (PARTITION BY label) AS cnt
    FROM train_test_split
    WHERE NOT is_test
)
SELECT
    doc_id,
    text,
    label,
    is_test,
    CASE
        WHEN rn < cnt * 1/3 THEN 0
        WHEN rn >= cnt * 1/3 AND rn < cnt * 2/3 THEN 1
        ELSE 2
    END AS folds_3_id,
    CASE
        WHEN rn < cnt * 0.2 THEN 0
        WHEN rn >= cnt * 0.2 AND rn < cnt * 0.4 THEN 1
        WHEN rn >= cnt * 0.4 AND rn < cnt * 0.6 THEN 2
        WHEN rn >= cnt * 0.6 AND rn < cnt * 0.8 THEN 3
        ELSE 4
    END AS folds_5_id,
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
    END AS folds_10_id
FROM train_set

UNION

SELECT
    doc_id,
    text,
    label,
    is_test,
    NULL AS folds_3_id,
    NULL AS folds_5_id,
    NULL AS folds_10_id
FROM train_test_split
WHERE is_test

ORDER BY doc_id
