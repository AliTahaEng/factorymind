"""Avro schemas for all Kafka topics."""

RAW_INSPECTION_SCHEMA = {
    "type": "record",
    "name": "RawInspection",
    "namespace": "com.factorymind",
    "fields": [
        {"name": "image_id",         "type": "string"},
        {"name": "camera_id",        "type": "string"},
        {"name": "product_category", "type": "string"},
        {"name": "image_bytes",      "type": "bytes"},
        {"name": "timestamp",        "type": "long"},
        {"name": "conveyor_speed",   "type": "float", "default": 1.0},
    ],
}

PROCESSED_RESULT_SCHEMA = {
    "type": "record",
    "name": "ProcessedResult",
    "namespace": "com.factorymind",
    "fields": [
        {"name": "image_id",           "type": "string"},
        {"name": "inspection_id",      "type": "string"},
        {"name": "defect_detected",    "type": "boolean"},
        {"name": "defect_type",        "type": ["null", "string"], "default": None},
        {"name": "confidence",         "type": "float"},
        {"name": "anomaly_score",      "type": "float"},
        {"name": "bounding_boxes",     "type": {
            "type": "array",
            "items": {
                "type": "record",
                "name": "BoundingBox",
                "fields": [
                    {"name": "x",          "type": "float"},
                    {"name": "y",          "type": "float"},
                    {"name": "w",          "type": "float"},
                    {"name": "h",          "type": "float"},
                    {"name": "label",      "type": "string"},
                    {"name": "confidence", "type": "float"},
                ],
            },
        }},
        {"name": "model_version",      "type": "string"},
        {"name": "processing_time_ms", "type": "int"},
        {"name": "timestamp",          "type": "long"},
    ],
}

MODEL_ALERT_SCHEMA = {
    "type": "record",
    "name": "ModelAlert",
    "namespace": "com.factorymind",
    "fields": [
        {"name": "alert_id",   "type": "string"},
        {"name": "alert_type", "type": {
            "type": "enum",
            "name": "AlertType",
            "symbols": ["HIGH_DEFECT_RATE", "MODEL_DRIFT", "LOW_ACCURACY", "PIPELINE_FAILURE"],
        }},
        {"name": "severity",   "type": {
            "type": "enum",
            "name": "Severity",
            "symbols": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        }},
        {"name": "message",    "type": "string"},
        {"name": "metadata",   "type": {"type": "map", "values": "string"}, "default": {}},
        {"name": "timestamp",  "type": "long"},
    ],
}

SYSTEM_EVENT_SCHEMA = {
    "type": "record",
    "name": "SystemEvent",
    "namespace": "com.factorymind",
    "fields": [
        {"name": "event_type",     "type": "string"},
        {"name": "source_service", "type": "string"},
        {"name": "payload",        "type": "string"},
        {"name": "timestamp",      "type": "long"},
    ],
}

TOPIC_SCHEMAS = {
    "raw-inspections":   RAW_INSPECTION_SCHEMA,
    "processed-results": PROCESSED_RESULT_SCHEMA,
    "model-alerts":      MODEL_ALERT_SCHEMA,
    "system-events":     SYSTEM_EVENT_SCHEMA,
}
