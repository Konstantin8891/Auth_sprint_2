"""Drop login history

Revision ID: ffcc27246a00
Revises: 7f97c78b0ae5
Create Date: 2025-04-13 13:38:40.697768

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ffcc27246a00"
down_revision: Union[str, None] = "7f97c78b0ae5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("login_history")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "login_history",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.UUID(), autoincrement=False, nullable=True),
        sa.Column("user_agent", sa.VARCHAR(length=250), autoincrement=False, nullable=True),
        sa.Column("host", sa.VARCHAR(length=250), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="login_history_user_id_fkey"),
        sa.PrimaryKeyConstraint("id", name="login_history_pkey"),
        sa.UniqueConstraint("id", name="login_history_id_uq"),
    )
    # ### end Alembic commands ###
