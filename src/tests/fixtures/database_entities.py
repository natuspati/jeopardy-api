import pytest
from factories.user import UserFactory
from sqlalchemy.ext.asyncio import AsyncSession

from api.authnetication import hash_password
from database.models.lobby import LobbyModel
from database.models.player import PlayerModel
from database.models.user import UserModel


@pytest.fixture
async def active_user(password: str, db_session: AsyncSession) -> UserModel:
    user = UserFactory.build(password=hash_password(password), is_active=True)
    db_session.add(user)
    return user


@pytest.fixture
async def inactive_user(password: str, db_session: AsyncSession) -> UserModel:
    user = UserFactory.build(password=hash_password(password), is_active=False)
    db_session.add(user)
    return user


@pytest.fixture
async def users(
    user_raw_data: tuple[dict, ...],
    db_session: AsyncSession,
) -> dict[str, list[UserModel]]:
    users = {"active": [], "inactive": []}
    for user_data in user_raw_data:
        user = UserModel(**user_data)
        db_session.add(user)
        if user.is_active:
            users["active"].append(user)
        else:
            users["inactive"].append(user)
    return users


@pytest.fixture
async def lobbies(
    lobby_raw_data: tuple[dict, dict, dict],
    db_session: AsyncSession,
) -> list[LobbyModel]:
    lobbies = []
    for lobby_data in lobby_raw_data:
        lobby = LobbyModel(**lobby_data)
        db_session.add(lobby)
        lobbies.append(lobby)
    return lobbies


@pytest.fixture
async def players(
    player_raw_data: list[dict],
    users: list[UserModel],
    lobbies: list[LobbyModel],
    db_session: AsyncSession,
) -> list[list[PlayerModel]]:
    players = [[] for _ in lobbies]
    for player_data in player_raw_data:
        player = PlayerModel(**player_data)
        db_session.add(player)

        lobby_id = player.lobby_id - 1
        players[lobby_id].append(player)
    return players
