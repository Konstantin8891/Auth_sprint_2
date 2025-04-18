"""Add login history table

Revision ID: 4c6343e3f053
Revises: ffcc27246a00
Create Date: 2025-04-13 13:44:56.035061

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4c6343e3f053"
down_revision: Union[str, None] = "ffcc27246a00"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "login_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("user_agent", sa.String(length=250), nullable=True),
        sa.Column("host", sa.String(length=250), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id", "created_at"),
        sa.UniqueConstraint("id", "created_at"),
        postgresql_partition_by="RANGE (created_at)",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("login_history")
    # ### end Alembic commands ###
