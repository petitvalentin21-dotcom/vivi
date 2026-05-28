"""create_stock_tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "batchs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("recette_id", sa.String(), nullable=True),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("portions_total", sa.Integer(), nullable=False),
        sa.Column("portions_restantes", sa.Integer(), nullable=False),
        sa.Column("date_cuisson", sa.Date(), nullable=False),
        sa.Column("date_peremption", sa.Date(), nullable=True),
        sa.Column("stockage", sa.String(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_batchs_nom"), "batchs", ["nom"], unique=False)

    op.create_table(
        "ingredients_base",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("nom", sa.String(), nullable=False),
        sa.Column("categorie", sa.String(), nullable=True),
        sa.Column("quantite", sa.Float(), nullable=True),
        sa.Column("unite", sa.String(), nullable=True),
        sa.Column("seuil_alerte", sa.Float(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingredients_base_nom"), "ingredients_base", ["nom"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_ingredients_base_nom"), table_name="ingredients_base")
    op.drop_table("ingredients_base")
    op.drop_index(op.f("ix_batchs_nom"), table_name="batchs")
    op.drop_table("batchs")
