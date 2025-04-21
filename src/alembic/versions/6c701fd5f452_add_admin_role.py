"""Add admin role

Revision ID: 6c701fd5f452
Revises: 4f01570df829
Create Date: 2025-04-13 18:59:51.376472

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6c701fd5f452"
down_revision: Union[str, None] = "4f01570df829"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO roles (id, name) VALUES ('b845266b-812a-49d5-8945-8426f21b789f', 'admin')")


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE id='b845266b-812a-49d5-8945-8426f21b789f'")
