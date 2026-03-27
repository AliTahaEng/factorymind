-- Staging model: clean defect detection records
SELECT
    id::uuid                AS detection_id,
    inspection_id::uuid,
    defect_type,
    confidence::float,
    bbox_x::float           AS x,
    bbox_y::float           AS y,
    bbox_w::float           AS w,
    bbox_h::float           AS h,
    model_version,
    created_at::timestamptz
FROM {{ source('factorymind', 'defect_detection_records') }}
WHERE inspection_id IS NOT NULL
