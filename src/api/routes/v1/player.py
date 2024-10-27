from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.dependencies import check_current_user_in_lobby, get_current_user
from api.interfaces import LobbyOperationsInterface
from api.schemas.authnetication import UserInTokenSchema
from api.schemas.nested.player import PlayerWithLinkShowSchema
from api.schemas.player import LobbyPlayerAddSchema
from exceptions.responses import UNAUTHORIZED_RESPONSE, generate_responses

player_router = APIRouter(
    prefix="/{lobby_id}/player",
    tags=["Player"],
)


@player_router.get(
    "/{player_id}/",
    response_model=PlayerWithLinkShowSchema,
    responses=generate_responses(
        (status.HTTP_400_BAD_REQUEST, "Player in not in the lobby"),
        UNAUTHORIZED_RESPONSE,
        (status.HTTP_403_FORBIDDEN, "Request user not in the lobby"),
        (status.HTTP_404_NOT_FOUND, "Player not found"),
    ),
    dependencies=[Depends(check_current_user_in_lobby)],
)
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


@player_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PlayerWithLinkShowSchema,
    responses=generate_responses(
        UNAUTHORIZED_RESPONSE,
        (status.HTTP_403_FORBIDDEN, "User is banned in the lobby"),
        (status.HTTP_409_CONFLICT, "Player already exists"),
        (status.HTTP_422_UNPROCESSABLE_ENTITY, "Player data invalid"),
    ),
)
async def create_player(
    lobby_id: int,
    lobby_player_add: LobbyPlayerAddSchema,
    user: Annotated[UserInTokenSchema, Depends(get_current_user)],
    integration_interface: Annotated[LobbyOperationsInterface, Depends()],
):
    """
    Create waiting player for a lobby.

    :param lobby_id: lobby id
    :param lobby_player_add: player create data
    :param user: current user
    :param integration_interface: integration interface
    :return: created player
    """
    return await integration_interface.create_waiting_player(
        lobby_id=lobby_id,
        user_id=user.user_id,
        lobby_player_add=lobby_player_add,
    )
