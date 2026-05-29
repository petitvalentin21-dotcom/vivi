"""add_preferences

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "preferences",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("cle", sa.String(200), nullable=False),
        sa.Column("valeur", sa.Text(), nullable=False),
        sa.Column("type_valeur", sa.String(20), nullable=False, server_default="string"),
        sa.Column("categorie", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_preferences_cle"), "preferences", ["cle"], unique=True)
    op.create_index(op.f("ix_preferences_categorie"), "preferences", ["categorie"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_preferences_categorie"), table_name="preferences")
    op.drop_index(op.f("ix_preferences_cle"), table_name="preferences")
    op.drop_table("preferences")
