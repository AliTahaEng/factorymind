-- Staging model: clean and type-cast raw inspections
SELECT
    id::uuid                                AS inspection_id,
    camera_id,
    product_category,
    image_s3_path,
    is_defective,
    anomaly_score::float                    AS anomaly_score,
    inspected_at::timestamptz               AS inspected_at,
    DATE_TRUNC('day', inspected_at)         AS inspection_date,
    DATE_TRUNC('hour', inspected_at)        AS inspection_hour
FROM {{ source('factorymind', 'inspections') }}
WHERE inspected_at IS NOT NULL
  AND camera_id IS NOT NULL
