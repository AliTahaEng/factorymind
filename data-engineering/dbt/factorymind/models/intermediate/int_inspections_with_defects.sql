-- Intermediate: join inspections with their defect counts
SELECT
    i.inspection_id,
    i.camera_id,
    i.product_category,
    i.is_defective,
    i.anomaly_score,
    i.inspected_at,
    i.inspection_date,
    i.inspection_hour,
    COUNT(d.detection_id)   AS defect_count,
    MAX(d.confidence)       AS max_defect_confidence,
    ARRAY_AGG(DISTINCT d.defect_type) FILTER (WHERE d.defect_type IS NOT NULL)
                            AS defect_types
FROM {{ ref('stg_inspections') }} i
LEFT JOIN {{ ref('stg_defect_detections') }} d ON i.inspection_id = d.inspection_id
GROUP BY
    i.inspection_id, i.camera_id, i.product_category,
    i.is_defective, i.anomaly_score, i.inspected_at,
    i.inspection_date, i.inspection_hour
