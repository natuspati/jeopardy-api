import pytest
from fastapi import Request

from api.services import LobbyService, PlayerService, RouteService, UserService
from api.services.pagination import PaginationService
from database.dals import LobbyDAL, PlayerDAL, UserDAL


@pytest.fixture
async def user_service(user_dal: UserDAL) -> UserService:
    return UserService(user_dal=user_dal)


@pytest.fixture
async def lobby_service(lobby_dal: LobbyDAL) -> LobbyService:
    return LobbyService(lobby_dal=lobby_dal)


@pytest.fixture
async def player_service(player_dal: PlayerDAL) -> PlayerService:
    return PlayerService(player_dal=player_dal)


@pytest.fixture
async def pagination_service(no_auth_request: Request) -> PaginationService:
    return PaginationService(request=no_auth_request)


@pytest.fixture
async def route_service(no_auth_request: Request) -> RouteService:
    return RouteService(request=no_auth_request)
