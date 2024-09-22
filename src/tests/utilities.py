import os
import random
import re
from typing import Any

from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Connection, text

from database.base_model import meta
from database.manager import create_database_connection_manager
from settings import APP_ROOT, settings


async def create_test_database(db_name: str) -> None:
    """
    Create test database.

    Drop test database if it exists.

    :param db_name: test database name
    :return:
    """
    db_manager = create_database_connection_manager(
        db_url=settings.db_url,
        db_isolation_level="AUTOCOMMIT",
    )
    create_db_query = text(f"CREATE DATABASE {db_name}")
    check_db_exists_query = text(
        f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'",
    )
    async with db_manager.connect() as conn:
        result = await conn.execute(check_db_exists_query)
        db_exists = result.scalar()
        if db_exists:
            await drop_test_database(db_name=db_name)
        else:
            await conn.execute(create_db_query)
    await db_manager.close()


async def drop_test_database(db_name: str) -> None:
    """
    Drop test database.

    :param db_name: test database name
    :return:
    """
    db_manager = create_database_connection_manager(
        db_url=settings.db_url,
        db_isolation_level="AUTOCOMMIT",
    )
    async with db_manager.connect() as conn:
        await conn.execute(
            text(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                + f"WHERE datname = '{db_name}'",
            ),
        )
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
    await db_manager.close()


def run_migrations(connection: Connection) -> None:
    """
    Run migrations on test database.

    :param connection: SQLAlchemy connection
    :return:
    """
    migrations_directory = os.path.join(APP_ROOT, "database/migrations")
    config = Config(APP_ROOT / "alembic.ini")
    config.set_main_option("script_location", migrations_directory)
    config.set_main_option("sqlalchemy.url", str(settings.db_url))
    script = ScriptDirectory.from_config(config)

    def upgrade(rev: str, ctx: EnvironmentContext):
        return script._upgrade_revs("head", rev)

    context = MigrationContext.configure(
        connection,
        opts={"target_metadata": meta, "fn": upgrade},
    )

    with context.begin_transaction():
        with Operations.context(context):
            context.run_migrations()


def normalize_sql(query: str) -> str:
    """
    Remove extra spaces from SQL query.

    :param query: SQL query
    :return: normalized SQL query
    """
    return re.sub(r"\s+", " ", query).strip().lower()


def check_queries_equivalent(
    reference_query: str,
    compare_query: str,
) -> bool:
    """
    Check if two SQL queries are equivalent.

    :param reference_query: reference SQL query
    :param compare_query: compare SQL query
    :return: whether two SQL queries are equivalent
    """
    return normalize_sql(reference_query) == normalize_sql(compare_query)


def choose_from_list(lst: list[Any]) -> Any:
    """
    Choose a random element from a list.

    :param lst: list of elements
    :return: random element in the list
    """
    return random.choice(lst)
