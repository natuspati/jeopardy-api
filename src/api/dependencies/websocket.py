from typing import Annotated, AsyncGenerator

from fastapi import Depends, WebSocket

from api.dependencies import get_current_player
from api.schemas.player import PlayerInDBSchema
from api.services import Connection, ConnectionManager, Room, ws_conn_manager


async def get_ws_connection_manager() -> ConnectionManager:
    """
    Get websocket connection manager.

    :return: websocket connection manager
    """
    return ws_conn_manager


async def get_lobby_room(
    lobby_id: int,
    conn_manager: Annotated[ConnectionManager, Depends(get_ws_connection_manager)],
) -> Room:
    """
    Get lobby room.

    :param lobby_id: lobby id
    :param conn_manager: websocket connection manager
    :return: lobby room
    """
    return conn_manager.get_or_create_room(room_id=lobby_id)


async def get_lobby_connection(
    lobby_room: Annotated[Room, Depends(get_lobby_room)],
    current_player: Annotated[PlayerInDBSchema, Depends(get_current_player)],
    conn_manager: Annotated[ConnectionManager, Depends(get_ws_connection_manager)],
    websocket: WebSocket,
) -> AsyncGenerator[Connection, None]:
    """
    Get lobby connection.

    :param lobby_room: lobby room
    :param current_player: current player
    :param conn_manager: websocket connection manager
    :param websocket: websocket connection
    :yield: connection to a lobby
    """
    connection = await conn_manager.create_connection(
        room_id=lobby_room.id,
        connection_id=current_player.id,
        websocket=websocket,
    )
    async with connection:
        yield connection
