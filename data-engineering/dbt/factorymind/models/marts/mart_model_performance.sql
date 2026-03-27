-- Mart: model performance over time (daily)
SELECT
    inspection_date,
    model_version,
    COUNT(*)                                        AS inspections_processed,
    SUM(CASE WHEN is_defective THEN 1 ELSE 0 END)  AS true_positives_approx,
    AVG(anomaly_score)                              AS avg_anomaly_score,
    PERCENTILE_CONT(0.5) WITHIN GROUP
        (ORDER BY anomaly_score)                    AS p50_anomaly_score,
    PERCENTILE_CONT(0.95) WITHIN GROUP
        (ORDER BY anomaly_score)                    AS p95_anomaly_score,
    NOW()                                           AS refreshed_at
FROM {{ ref('int_inspections_with_defects') }} i
JOIN {{ ref('stg_defect_detections') }} d
    ON i.inspection_id = d.inspection_id
GROUP BY inspection_date, model_version
ORDER BY inspection_date DESC
