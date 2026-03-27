"""Test ORM model structure."""
import pytest
from api_service.models.db_models import User, Inspection, DefectDetectionRecord, ModelVersion


def test_user_model_has_required_columns():
    cols = {c.name for c in User.__table__.columns}
    assert "id" in cols
    assert "username" in cols
    assert "hashed_password" in cols
    assert "role" in cols
    assert "is_active" in cols
    assert "created_at" in cols


def test_inspection_model_has_required_columns():
    cols = {c.name for c in Inspection.__table__.columns}
    assert "id" in cols
    assert "inspection_id" in cols
    assert "camera_id" in cols
    assert "is_defective" in cols
    assert "defect_score" in cols
    assert "anomaly_score" in cols
    assert "processing_time_ms" in cols
    assert "inspected_at" in cols


def test_model_version_has_status_column():
    cols = {c.name for c in ModelVersion.__table__.columns}
    assert "model_name" in cols
    assert "version" in cols
    assert "status" in cols
    assert "promoted_at" in cols
