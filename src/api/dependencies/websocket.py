from typing import Annotated

from fastapi import Depends, WebSocket

from api.dependencies import get_current_user_from_header
from api.schemas.user import UserInDBSchema
from api.services import PlayerService, ws_conn_manager
from cutom_types.websocket import ROOM_CONNECTION_TYPE
from exceptions.service.not_found import PlayerNotFoundError


async def get_lobby_room(
    lobby_id: int,
    websocket: WebSocket,
    current_user: Annotated[UserInDBSchema, Depends(get_current_user_from_header)],
    player_service: Annotated[PlayerService, Depends()],
) -> ROOM_CONNECTION_TYPE:
    """
    Get lobby room and player connection.

    Room and player are fetched from authorization header.

    :param lobby_id: lobby id
    :param websocket: websocket
    :param current_user: current user
    :param player_service: player service
    :return: room and connection for the player
    """
    player = await player_service.get_player_by_user_lobby(
        user_id=current_user.id,
        lobby_id=lobby_id,
    )
    if not player:
        raise PlayerNotFoundError()
    connection = ws_conn_manager.create_connection(
        room_id=lobby_id,
        connection_id=player.id,
        websocket=websocket,
    )
    room = ws_conn_manager.get_room(lobby_id, raise_error=True)
    return room, connection
