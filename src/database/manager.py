import contextlib
import logging
from typing import AsyncIterator

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from cutom_types.database import ISOLATION_LEVEL_TYPE
from exceptions.service.database import DatabaseSessionManagerNotInitializedError
from settings import settings

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    def __init__(
        self,
        db_url: str | URL,
        db_echo: bool = False,
        db_echo_pool: bool = False,
        db_isolation_level: ISOLATION_LEVEL_TYPE = "READ COMMITTED",
        db_expire_on_commit: bool = False,
        rollback: bool = False,
    ):
        self._engine = create_async_engine(
            url=db_url,
            echo=db_echo,
            echo_pool=db_echo_pool,
            isolation_level=db_isolation_level,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=db_expire_on_commit,
        )
        self._rollback = rollback

    async def close(self) -> None:
        """
        Close session to database.

        :return:
        """
        if self._engine is None:
            raise DatabaseSessionManagerNotInitializedError()
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        Connect to database.

        :yield: database connection
        """
        if self._engine is None:
            raise DatabaseSessionManagerNotInitializedError()

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception as error:
                logger.exception(
                    "An exception was raised during connection",
                    exc_info=error,
                )
                await connection.rollback()
                raise error
            else:
                if self._rollback:
                    await connection.rollback()

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:  # noqa: WPS231
        """
        Create session to database.

        If `_rollback` is True, all transactions are rolled back. By default,
        transactions are rolled back if Exception occurs.

        :yield: database session
        """
        if self._sessionmaker is None:
            raise DatabaseSessionManagerNotInitializedError()

        async with self._sessionmaker() as session, session.begin():  # noqa: WPS316
            try:
                yield session
            except Exception as error:
                logger.exception(
                    "An exception was raised during session",
                    exc_info=error,
                )
                await session.rollback()
                raise error
            else:
                if self._rollback:
                    await session.rollback()


def create_database_connection_manager(
    db_url: str | URL = None,
    db_echo: bool | None = None,
    db_echo_pool: bool | None = None,
    db_isolation_level: ISOLATION_LEVEL_TYPE | None = None,
    db_expire_on_commit: bool | None = None,
    rollback: bool = False,
) -> DatabaseConnectionManager:
    """
    Create and return a new DatabaseConnectionManager instance.

    This function initializes a DatabaseSessionManager with specified database
    settings. If a specific setting is not provided, it defaults to the corresponding
    value defined in the settings module.

    :param db_url: database URL to connect to
    :param db_echo: if True, the engine will log all statements
    :param db_echo_pool: if True, the connection pool will log all checkouts/checkins
    :param db_isolation_level: isolation level for database transactions
    :param db_expire_on_commit: if True, all instances will be expired after each commit
    :param rollback: if True, all changes are be rolled back in connection or session
    :return: configured instance of DatabaseSessionManager
    """
    return DatabaseConnectionManager(
        db_url=db_url or settings.db_url,
        db_echo=db_echo or settings.db_echo,
        db_echo_pool=db_echo_pool or settings.db_echo_pool,
        db_isolation_level=db_isolation_level or settings.db_isolation_level,
        db_expire_on_commit=db_expire_on_commit or settings.db_expire_on_commit,
        rollback=rollback,
    )


default_db_manager = create_database_connection_manager()
