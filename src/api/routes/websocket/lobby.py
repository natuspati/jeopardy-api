from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_current_player, get_lobby_connection, get_lobby_room
from api.messages import LobbyConnectMessage, UserMessage
from api.schemas.player import PlayerInDBSchema
from api.services import Connection, Room

lobby_router = APIRouter(prefix="/lobby", tags=["Lobby"])


@lobby_router.websocket("/{lobby_id}")
async def join_lobby(
    current_player: Annotated[PlayerInDBSchema, Depends(get_current_player)],
    room: Annotated[Room, Depends(get_lobby_room)],
    connection: Annotated[Connection, Depends(get_lobby_connection)],
):
    """
    Join lobby.

    :param current_player: current player from authorization header.
    :param room: lobby room
    :param connection: lobby connection
    :return:
    """
    await room.send(LobbyConnectMessage(player_id=current_player.id))
    async for message in connection:
        user_message = UserMessage(sender=current_player.id, **message)
        await room.send(user_message, connection_ids=user_message.receivers)
