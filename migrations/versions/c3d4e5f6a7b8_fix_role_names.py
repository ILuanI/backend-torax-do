"""align role names with application constants

Revision ID: c3d4e5f6a7b8
Revises: a1b2c3d4e5f6
Create Date: 2026-06-13 18:00:00.000000
"""

from alembic import op

revision = "c3d4e5f6a7b8"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE roles SET nombre = 'especialista' WHERE nombre = 'medico'")
    op.execute("UPDATE roles SET nombre = 'admin' WHERE nombre = 'administrador'")


def downgrade() -> None:
    op.execute("UPDATE roles SET nombre = 'medico' WHERE nombre = 'especialista'")
    op.execute("UPDATE roles SET nombre = 'administrador' WHERE nombre = 'admin'")
