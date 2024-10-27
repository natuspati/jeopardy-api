import asyncio
import logging
from contextlib import ExitStack
from typing import AsyncGenerator, Generator

import pytest
from factories.token import UserTokenFactory
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession
from utilities import drop_test_database, recreate_test_database

from api.dependencies import get_current_user
from api.dependencies.websocket import get_ws_connection_manager
from api.services import ConnectionManager
from application import get_app
from database.dependencies import get_db_manager
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
async def fastapi_app(test_db_url: URL) -> Generator[FastAPI, None, None]:
    """
    Fast API application with external services mocked or used test instances.

    :param test_db_url: test database url
    :yield: FastAPI application
    """
    with ExitStack():
        app = get_app()
        test_db_manager = create_database_connection_manager(
            db_url=test_db_url,
        )
        app.dependency_overrides[get_db_manager] = lambda: test_db_manager
        yield app


@pytest.fixture(scope="session")
async def _setup_database(test_db_url: URL) -> None:
    await recreate_test_database(test_db_url)
    yield
    await drop_test_database(test_db_url.database)


@pytest.fixture
async def _reset_database(test_db_url: URL) -> AsyncGenerator[None, None]:
    yield
    await recreate_test_database(test_db_url)


@pytest.fixture
async def db_manager(
    _setup_database: None,
    test_db_url: URL,
) -> AsyncGenerator[DatabaseConnectionManager, None]:
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


@pytest.fixture
async def scope(fastapi_app: FastAPI) -> dict:
    return {
        "type": "http",
        "http_version": "1.1",
        "root_path": "",
        "path": "/test",
        "raw_path": b"/test",
        "query_string": b"",
        "headers": [],
        "app": fastapi_app,
    }


@pytest.fixture
async def no_auth_request(scope: dict) -> Request:
    return Request(scope)


@pytest.fixture(scope="session")
async def ws_conn_manager() -> ConnectionManager:
    return ConnectionManager()


@pytest.fixture
async def http_client(
    fastapi_app: FastAPI,
    ws_conn_manager: ConnectionManager,
) -> TestClient:
    fastapi_app.dependency_overrides[get_ws_connection_manager] = (
        lambda: ws_conn_manager
    )
    return TestClient(fastapi_app)


@pytest.fixture
async def auth_client(
    fastapi_app: FastAPI,
    ws_conn_manager: ConnectionManager,
) -> TestClient:
    user_in_token = UserTokenFactory.build(is_active=True)
    fastapi_app.dependency_overrides[get_ws_connection_manager] = (
        lambda: ws_conn_manager
    )
    fastapi_app.dependency_overrides[get_current_user] = lambda: user_in_token
    return TestClient(fastapi_app)
