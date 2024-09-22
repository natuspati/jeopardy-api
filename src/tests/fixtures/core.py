import asyncio
import logging
from contextlib import ExitStack
from typing import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from utilities import create_test_database, drop_test_database, run_migrations

from application import get_app
from database.manager import (
    DatabaseConnectionManager,
    create_database_connection_manager,
)

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop(request) -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def fastapi_app() -> Generator[FastAPI, None, None]:
    with ExitStack():
        yield get_app()


@pytest.fixture(scope="session")
async def _setup_database(test_db_url: URL) -> None:
    # Create test database
    await create_test_database(test_db_url.database)

    # Apply migrations to test database
    test_db_manager = create_database_connection_manager(test_db_url)
    async with test_db_manager.connect() as connection:
        await connection.run_sync(run_migrations)
    await test_db_manager.close()

    yield

    # Drop test database
    await drop_test_database(test_db_url.database)


@pytest.fixture
async def db_manager(
    _setup_database: None,
    test_db_url: URL,
) -> AsyncGenerator[AsyncEngine, None]:
    test_db_manager = create_database_connection_manager(
        db_url=test_db_url,
        rollback=True,
    )
    yield test_db_manager
    await test_db_manager.close()


@pytest.fixture
async def db_session(
    db_manager: DatabaseConnectionManager,
) -> AsyncGenerator[AsyncSession, None]:
    async with db_manager.session() as session:
        yield session
