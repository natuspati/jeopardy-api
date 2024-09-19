"""Create lobby, user, player tables.

Revision ID: 0001
Revises: 
Create Date: 2024-09-17 15:27:57.666787

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lobby",
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lobby_id"), "lobby", ["id"], unique=False)

    op.create_table(
        "user",
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "modified_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_id"), "user", ["id"], unique=False)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=False)
    op.execute(
        """
            CREATE OR REPLACE FUNCTION update_modified_at()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.modified_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """,
    )
    op.execute(
        """
                CREATE TRIGGER update_modified_at_trigger
                BEFORE UPDATE ON "user"
                FOR EACH ROW
                EXECUTE FUNCTION update_modified_at();
            """,
    )

    op.create_table(
        "player",
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column(
            "state",
            sa.Enum(
                "lead",
                "waiting",
                "playing",
                "inactive",
                "banned",
                name="playerstateenum",
            ),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lobby_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["lobby_id"],
            ["lobby.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_player_id"), "player", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_player_id"), table_name="player")
    op.drop_table("player")

    op.execute("DROP TRIGGER IF EXISTS update_modified_at_trigger ON 'user';")
    op.execute("DROP FUNCTION IF EXISTS update_modified_at();")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_index(op.f("ix_user_id"), table_name="user")
    op.drop_table("user")

    op.drop_index(op.f("ix_lobby_id"), table_name="lobby")
    op.drop_table("lobby")
