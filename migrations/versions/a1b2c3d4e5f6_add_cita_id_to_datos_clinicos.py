"""add cita_id to datos_clinicos

Revision ID: a1b2c3d4e5f6
Revises: 44d66f6f0f1f
Create Date: 2026-06-14 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "44d66f6f0f1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("datos_clinicos", sa.Column("cita_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_datos_clinicos_cita_id"), "datos_clinicos", ["cita_id"], unique=False)
    op.create_foreign_key(
        "fk_datos_clinicos_cita_id",
        "datos_clinicos",
        "citas",
        ["cita_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_datos_clinicos_cita_id", "datos_clinicos", type_="foreignkey")
    op.drop_index(op.f("ix_datos_clinicos_cita_id"), table_name="datos_clinicos")
    op.drop_column("datos_clinicos", "cita_id")
