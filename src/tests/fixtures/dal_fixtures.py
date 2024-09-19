import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from database.dals import UserDAL
from database.manager import DatabaseConnectionManager


@pytest.fixture
async def user_dal(
    db_session: AsyncSession,
    db_manager: DatabaseConnectionManager,
) -> UserDAL:
    return UserDAL(db_session=db_session, db_manager=db_manager)
