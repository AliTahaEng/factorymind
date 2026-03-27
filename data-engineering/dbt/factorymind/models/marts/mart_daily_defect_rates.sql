-- Mart: daily defect rates by camera and product category
SELECT
    inspection_date,
    camera_id,
    product_category,
    COUNT(*)                                        AS total_inspections,
    SUM(CASE WHEN is_defective THEN 1 ELSE 0 END)  AS defective_count,
    ROUND(
        SUM(CASE WHEN is_defective THEN 1 ELSE 0 END)::numeric
        / NULLIF(COUNT(*), 0) * 100,
        2
    )                                               AS defect_rate_pct,
    AVG(anomaly_score)                              AS avg_anomaly_score,
    MAX(anomaly_score)                              AS max_anomaly_score,
    NOW()                                           AS refreshed_at
FROM {{ ref('int_inspections_with_defects') }}
GROUP BY inspection_date, camera_id, product_category
ORDER BY inspection_date DESC, defect_rate_pct DESC
