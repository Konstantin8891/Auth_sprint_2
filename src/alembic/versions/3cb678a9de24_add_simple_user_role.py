"""Add simple user role

Revision ID: 3cb678a9de24
Revises: 051e68b09a25
Create Date: 2025-03-16 17:38:50.584640

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3cb678a9de24"
down_revision: Union[str, None] = "051e68b09a25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO roles (id, name) VALUES ('4f01df67-ede6-41b3-86be-95454892b72a', 'user')")


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE id='4f01df67-ede6-41b3-86be-95454892b72a'")
