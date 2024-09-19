from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import (
    get_current_user,
    get_date_parameters,
    get_order_parameter,
    get_pagination_parameters,
)
from api.interfaces import LobbyOperationsInterface
from api.routes.v1.player import player_router
from api.schemas.lobby import PaginatedLobbiesSchema
from api.schemas.nested.player import LobbyWithPlayersScowSchema
from api.schemas.query import DateTimeSchema, OrderSchema, PaginationSchema

lobby_router = APIRouter(
    prefix="/lobby",
    tags=["Lobby"],
    dependencies=[Depends(get_current_user)],
)
lobby_router.include_router(player_router)


@lobby_router.get("/", response_model=PaginatedLobbiesSchema)
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


@lobby_router.get("/{lobby_id}", response_model=LobbyWithPlayersScowSchema)
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
