import asyncio
import os
from contextlib import ExitStack
from typing import Generator

import pytest
from alembic.config import Config
from alembic.operations import Operations
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import FastAPI
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncSession

from application import get_app
from database.base_model import meta
from database.manager import (
    DatabaseConnectionManager,
    create_database_connection_manager,
)
from database.manager import db_manager as persistent_db_manager
from settings import APP_ROOT, settings


@pytest.fixture(scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def fastapi_app() -> Generator[FastAPI, None, None]:
    with ExitStack():
        yield get_app()


@pytest.fixture(scope="session", autouse=True)
async def _setup_database() -> None:
    def run_migrations(conn: Connection) -> None:
        migrations_directory = os.path.join(APP_ROOT, "database/migrations")
        config = Config(APP_ROOT / "alembic.ini")
        config.set_main_option("script_location", migrations_directory)
        config.set_main_option("sqlalchemy.url", str(settings.db_url))
        script = ScriptDirectory.from_config(config)

        def upgrade(rev: str, ctx: EnvironmentContext):
            return script._upgrade_revs("head", rev)

        context = MigrationContext.configure(
            conn,
            opts={"target_metadata": meta, "fn": upgrade},
        )

        with context.begin_transaction():
            with Operations.context(context):
                context.run_migrations()

    async with persistent_db_manager.connect() as connection:
        await connection.run_sync(run_migrations)
    await persistent_db_manager.close()


@pytest.fixture
async def db_manager() -> DatabaseConnectionManager:
    non_persistent_db_manager = create_database_connection_manager(rollback=True)
    yield non_persistent_db_manager
    await non_persistent_db_manager.close()


@pytest.fixture
async def db_session(db_manager: DatabaseConnectionManager) -> AsyncSession:
    async with db_manager.session() as session:
        yield session
