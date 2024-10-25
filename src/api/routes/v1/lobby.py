from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.dependencies import (
    check_current_user_in_lobby,
    get_current_user,
    get_date_parameters,
    get_order_parameter,
    get_pagination_parameters,
)
from api.interfaces import LobbyOperationsInterface
from api.routes.v1.player import player_router
from api.schemas.lobby import LobbyPlayerCreateSchema, PaginatedLobbiesSchema
from api.schemas.nested.player import LobbyWithPlayersScowSchema
from api.schemas.query import DateTimeSchema, OrderSchema, PaginationSchema
from api.schemas.user import UserInDBSchema
from exceptions.responses import UNAUTHORIZED_RESPONSE, generate_responses

lobby_router = APIRouter(prefix="/lobby", tags=["Lobby"])
lobby_router.include_router(player_router)


@lobby_router.get(
    "/",
    response_model=PaginatedLobbiesSchema,
    responses=generate_responses(UNAUTHORIZED_RESPONSE),
    dependencies=[Depends(get_current_user)],
)
async def get_lobbies(
    pagination: Annotated[PaginationSchema, Depends(get_pagination_parameters)],
    date: Annotated[DateTimeSchema, Depends(get_date_parameters)],
    order: Annotated[OrderSchema, Depends(get_order_parameter)],
    integration_interface: Annotated[LobbyOperationsInterface, Depends()],
):
    """
    Get list of lobbies.

    :param pagination: pagination query parameters
    :param date: date query parameters
    :param order: order by query parameter
    :param integration_interface: lobby operations interface
    :return: paginated list of lobbies
    """
    return await integration_interface.get_lobbies(
        pagination=pagination,
        date=date,
        order=order,
    )


@lobby_router.get(
    "/{lobby_id}",
    response_model=LobbyWithPlayersScowSchema,
    responses=generate_responses(
        UNAUTHORIZED_RESPONSE,
        (status.HTTP_403_FORBIDDEN, "Request user not in the lobby"),
        (status.HTTP_404_NOT_FOUND, "Lobby not found"),
    ),
    dependencies=[Depends(check_current_user_in_lobby)],
)
async def get_lobby(
    lobby_id: int,
    integration_interface: Annotated[LobbyOperationsInterface, Depends()],
):
    """
    Get lobby details with associated players.

    :param lobby_id: lobby id
    :param integration_interface: lobby operations interface
    :return: lobby details with associated players
    """
    return await integration_interface.get_lobby(lobby_id)


@lobby_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=LobbyWithPlayersScowSchema,
    responses=generate_responses(
        UNAUTHORIZED_RESPONSE,
        (status.HTTP_422_UNPROCESSABLE_ENTITY, "Lobby data invalid"),
    ),
)
async def create_lobby(
    lobby_player_create_schema: LobbyPlayerCreateSchema,
    user: Annotated[UserInDBSchema, Depends(get_current_user)],
    integration_interface: Annotated[LobbyOperationsInterface, Depends()],
):
    """
    Create lobby and assign current user as its lead.

    :param lobby_player_create_schema: lobby and player create data
    :param user: current user
    :param integration_interface: integration interface
    :return: created lobby with lead player
    """
    return await integration_interface.create_lobby(
        user_id=user.id,
        lobby_player_create=lobby_player_create_schema,
    )
