"""
Add unique constraint for player table.

Revision ID: 0002
Revises: 0001
Create Date: 2024-10-19 19:49:56.753017

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_lobby_user", "player", ["lobby_id", "user_id"])


def downgrade() -> None:
    op.drop_constraint("uq_lobby_user", "player", type_="unique")
