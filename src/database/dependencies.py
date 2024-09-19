from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from database.manager import DatabaseConnectionManager, db_manager


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """
    Get database session.

    :yield: asynchronous database session
    """
    async with db_manager.session() as session:
        yield session


async def get_db_manager() -> DatabaseConnectionManager:
    """
    Get database manager.

    :return: database manager
    """
    return db_manager
