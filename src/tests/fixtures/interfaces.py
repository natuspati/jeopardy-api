import pytest

from api.interfaces import LobbyOperationsInterface, UserOperationsInterface
from api.services import (
    ConnectionManager,
    LobbyService,
    PlayerService,
    RouteService,
    UserService,
)
from api.services.pagination import PaginationService


@pytest.fixture
async def user_operations(
    user_service: UserService,
    lobby_service: LobbyService,
    pagination_service: PaginationService,
) -> UserOperationsInterface:
    return UserOperationsInterface(
        user_service=user_service,
        lobby_service=lobby_service,
        pagination_service=pagination_service,
    )


@pytest.fixture
async def lobby_operations(
    lobby_service: LobbyService,
    player_service: PlayerService,
    pagination_service: PaginationService,
    ws_conn_manager: ConnectionManager,
    route_service: RouteService,
) -> LobbyOperationsInterface:
    return LobbyOperationsInterface(
        lobby_service=lobby_service,
        player_service=player_service,
        pagination_service=pagination_service,
        conn_manager=ws_conn_manager,
        route_service=route_service,
    )
