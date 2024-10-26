from typing import Annotated

from fastapi import Depends, WebSocket

from api.dependencies import get_current_player
from api.schemas.player import PlayerInDBSchema
from api.services import Connection, Room, ws_conn_manager


async def get_lobby_room(lobby_id: int) -> Room:
    """
    Get lobby room.

    :param lobby_id: lobby id
    :return: lobby room
    """
    return ws_conn_manager.get_or_create_room(room_id=lobby_id)


async def get_lobby_connection(
    lobby_room: Annotated[Room, Depends(get_lobby_room)],
    current_player: Annotated[PlayerInDBSchema, Depends(get_current_player)],
    websocket: WebSocket,
) -> Connection:
    """
    Get lobby connection.

    :param lobby_room: lobby room
    :param current_player: current player
    :param websocket: websocket connection
    :return: connection to a lobby
    """
    return ws_conn_manager.create_connection(
        room_id=lobby_room.id,
        connection_id=current_player.id,
        websocket=websocket,
    )
