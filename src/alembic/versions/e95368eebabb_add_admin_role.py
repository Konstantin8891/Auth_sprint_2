"""Add admin role

Revision ID: e95368eebabb
Revises: 369a4e567e9d
Create Date: 2025-03-07 21:06:16.212588

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e95368eebabb"
down_revision: Union[str, None] = "369a4e567e9d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO roles (id, name) VALUES ('b845266b-812a-49d5-8945-8426f21b789f', 'admin')")


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE id='b845266b-812a-49d5-8945-8426f21b789f'")
