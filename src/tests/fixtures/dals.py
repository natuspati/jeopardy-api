import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.dals import LobbyDAL, PlayerDAL, UserDAL
from database.manager import DatabaseConnectionManager


@pytest.fixture
async def user_dal(
    db_session: AsyncSession,
    db_manager: DatabaseConnectionManager,
) -> UserDAL:
    return UserDAL(db_session=db_session, db_manager=db_manager)


@pytest.fixture
async def lobby_dal(
    db_session: AsyncSession,
    db_manager: DatabaseConnectionManager,
) -> LobbyDAL:
    return LobbyDAL(db_session=db_session, db_manager=db_manager)


@pytest.fixture
async def player_dal(
    db_session: AsyncSession,
    db_manager: DatabaseConnectionManager,
) -> PlayerDAL:
    return PlayerDAL(db_session=db_session, db_manager=db_manager)
