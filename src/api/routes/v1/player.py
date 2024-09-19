from typing import Annotated

from fastapi import APIRouter, Depends

from api.interfaces import LobbyOperationsInterface
from api.schemas.nested.player import PlayerWithLobbyUseShowSchema

player_router = APIRouter(prefix="/{lobby_id}/player", tags=["Player"])


@player_router.get("/{player_id}/", response_model=PlayerWithLobbyUseShowSchema)
async def get_player(
    lobby_id: int,
    player_id: int,
    integration_interface: Annotated[LobbyOperationsInterface, Depends()],
):
    """
    Get player details with associated user and lobby information.

    :param lobby_id: lobby id
    :param player_id: player id
    :param integration_interface: lobby operations interface
    :return: player with user and lobby informationW
    """
    return await integration_interface.get_player(
        lobby_id=lobby_id,
        player_id=player_id,
    )
