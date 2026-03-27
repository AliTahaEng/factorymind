"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "inspections",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("inspection_id", sa.String(64), nullable=False),
        sa.Column("image_id", sa.String(64), nullable=False),
        sa.Column("camera_id", sa.String(64), nullable=False),
        sa.Column("product_id", sa.String(64), nullable=True),
        sa.Column("is_defective", sa.Boolean, nullable=False),
        sa.Column("defect_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("anomaly_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("classification_label", sa.String(128), nullable=True),
        sa.Column("bounding_boxes", sa.JSON, nullable=True),
        sa.Column("processing_time_ms", sa.Integer, nullable=False, server_default="0"),
        sa.Column("model_version", sa.String(64), nullable=True),
        sa.Column("inspected_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("inspection_id"),
    )
    op.create_index("ix_inspections_image_id", "inspections", ["image_id"])
    op.create_index("ix_inspections_inspected_at", "inspections", ["inspected_at"])
    op.create_table(
        "defect_detections",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("inspection_id", sa.String(64), nullable=False),
        sa.Column("defect_type", sa.String(128), nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("x", sa.Float, nullable=True),
        sa.Column("y", sa.Float, nullable=True),
        sa.Column("w", sa.Float, nullable=True),
        sa.Column("h", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("model_name", sa.String(128), nullable=False),
        sa.Column("version", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="staging"),
        sa.Column("mlflow_run_id", sa.String(64), nullable=True),
        sa.Column("accuracy", sa.Float, nullable=True),
        sa.Column("f1_score", sa.Float, nullable=True),
        sa.Column("promoted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("model_versions")
    op.drop_table("defect_detections")
    op.drop_table("inspections")
    op.drop_table("users")
