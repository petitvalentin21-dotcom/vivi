"""create_courses_tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "listes_courses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("statut", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listes_courses_nom"), "listes_courses", ["nom"], unique=False)

    op.create_table(
        "items_courses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("liste_id", sa.String(), nullable=False),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("quantite", sa.Float(), nullable=True),
        sa.Column("unite", sa.String(), nullable=True),
        sa.Column("categorie", sa.String(), nullable=True),
        sa.Column("recette_id", sa.String(), nullable=True),
        sa.Column("achete", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_items_courses_nom"), "items_courses", ["nom"], unique=False)
    op.create_index(op.f("ix_items_courses_liste_id"), "items_courses", ["liste_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_items_courses_liste_id"), table_name="items_courses")
    op.drop_index(op.f("ix_items_courses_nom"), table_name="items_courses")
    op.drop_table("items_courses")
    op.drop_index(op.f("ix_listes_courses_nom"), table_name="listes_courses")
    op.drop_table("listes_courses")
