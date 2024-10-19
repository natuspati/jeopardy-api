from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.manager import DatabaseConnectionManager, default_db_manager


async def get_db_manager() -> DatabaseConnectionManager:
    """
    Get database manager.

    :return: database manager
    """
    return default_db_manager


async def get_db_session(
    db_manager: DatabaseConnectionManager = Depends(get_db_manager),
) -> AsyncIterator[AsyncSession]:
    """
    Get database session.

    :yield: asynchronous database session
    """
    async with db_manager.session() as session:
        yield session
