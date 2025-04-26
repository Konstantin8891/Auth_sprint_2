"""Add social network record

Revision ID: bb370f044d6f
Revises: 3d6c57f43146
Create Date: 2025-04-26 02:04:49.271076

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bb370f044d6f"
down_revision: Union[str, None] = "3d6c57f43146"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("INSERT INTO social_network (id, name) VALUES ('10dac462-cd27-48b7-8e99-28b848266204', 'yandex')")


def downgrade() -> None:
    op.execute("DELETE FROM social_network WHERE id='10dac462-cd27-48b7-8e99-28b848266204'")
