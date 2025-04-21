"""Add user role

Revision ID: 4355c3405022
Revises: 0af92f30f3ae
Create Date: 2025-04-13 18:57:36.537666

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4355c3405022"
down_revision: Union[str, None] = "0af92f30f3ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO roles (id, name) VALUES ('4f01df67-ede6-41b3-86be-95454892b72a', 'user')")


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE id='4f01df67-ede6-41b3-86be-95454892b72a'")
