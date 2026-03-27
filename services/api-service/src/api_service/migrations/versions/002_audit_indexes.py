"""Add audit_logs table and performance indexes

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("path", sa.String(512), nullable=False),
        sa.Column("query", sa.String(1024), nullable=True),
        sa.Column("status_code", sa.Integer, nullable=False),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(512), nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("ix_inspections_camera_id", "inspections", ["camera_id"])
    op.create_index("ix_inspections_is_defective", "inspections", ["is_defective"])
    op.create_index("ix_model_versions_status", "model_versions", ["status"])


def downgrade() -> None:
    op.drop_index("ix_model_versions_status")
    op.drop_index("ix_inspections_is_defective")
    op.drop_index("ix_inspections_camera_id")
    op.drop_index("ix_audit_logs_timestamp")
    op.drop_index("ix_audit_logs_user_id")
    op.drop_table("audit_logs")
