import pytest

from api.interfaces import LobbyOperationsInterface, UserOperationsInterface
from api.services import LobbyService, PlayerService, UserService
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
) -> LobbyOperationsInterface:
    return LobbyOperationsInterface(
        lobby_service=lobby_service,
        player_service=player_service,
        pagination_service=pagination_service,
    )
