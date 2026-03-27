"""Seed default admin user

Revision ID: 003
Revises: 002
Create Date: 2024-01-03 00:00:00.000000

Default credentials:
  admin    / admin
  operator / operator

IMPORTANT: Change passwords before any production deployment.
"""
from typing import Sequence, Union
import uuid
from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _hash(password: str) -> str:
    from passlib.context import CryptContext
    return CryptContext(schemes=["bcrypt"], deprecated="auto").hash(password)


def upgrade() -> None:
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT COUNT(*) FROM users"))
    if result.scalar() == 0:
        conn.execute(
            sa.text(
                "INSERT INTO users (id, username, email, hashed_password, role, is_active) "
                "VALUES (:id, :username, :email, :pw, :role, true)"
            ),
            {"id": str(uuid.uuid4()), "username": "admin",
             "email": "admin@factorymind.local", "pw": _hash("admin"), "role": "admin"},
        )
        conn.execute(
            sa.text(
                "INSERT INTO users (id, username, email, hashed_password, role, is_active) "
                "VALUES (:id, :username, :email, :pw, :role, true)"
            ),
            {"id": str(uuid.uuid4()), "username": "operator",
             "email": "operator@factorymind.local", "pw": _hash("operator"), "role": "operator"},
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM users WHERE username IN ('admin', 'operator')"))
