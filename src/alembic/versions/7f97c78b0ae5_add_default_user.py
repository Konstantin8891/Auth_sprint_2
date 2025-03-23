"""Add default user

Revision ID: 7f97c78b0ae5
Revises: 3cb678a9de24
Create Date: 2025-03-22 12:28:52.197929

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f97c78b0ae5"
down_revision: Union[str, None] = "3cb678a9de24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "INSERT INTO users (id, login, password, first_name, last_name) VALUES ('ee1fd13b-ba1b-4f7c-9948-5154597e12c1', 'default_user', 'scrypt:32768:8:1$BUvQJ16qwPsZgJEB$64807aaaf86cec329ac0a34dfee875785e9b23da8c820609e1254f9819f87eed0e2e80db8e0e2226ac58fcbbcec351ca08ad3b199113cb53f86235a46607edfe', 'Имя', 'Фамилия')"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM users WHERE id='ee1fd13b-ba1b-4f7c-9948-5154597e12c1'"))
