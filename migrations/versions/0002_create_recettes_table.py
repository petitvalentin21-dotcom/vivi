"""create_recettes_table

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-28

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recettes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("titre", sa.String(), nullable=False),
        sa.Column("ingredients", sa.JSON(), nullable=True),
        sa.Column("etapes", sa.JSON(), nullable=True),
        sa.Column("portions", sa.Integer(), nullable=False),
        sa.Column("temps_prep_min", sa.Integer(), nullable=True),
        sa.Column("temps_cuisson_min", sa.Integer(), nullable=True),
        sa.Column("conservation_jours", sa.Integer(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("notes_perso", sa.String(), nullable=True),
        sa.Column("statut_valeur_sure", sa.Boolean(), nullable=False),
        sa.Column("nb_fois_cuisinee", sa.Integer(), nullable=False),
        sa.Column("derniere_fois_cuisinee", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recettes_titre"), "recettes", ["titre"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_recettes_titre"), table_name="recettes")
    op.drop_table("recettes")
