from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_lobby_room
from cutom_types.websocket import ROOM_CONNECTION_TYPE

lobby_router = APIRouter(prefix="/lobby", tags=["Lobby"])


@lobby_router.websocket("/{lobby_id}")
async def join_lobby(
    room_connection: Annotated[ROOM_CONNECTION_TYPE, Depends(get_lobby_room)]
):
    room, connection = room_connection[0], room_connection[1]
    async with connection:
        async for message in connection:
            await room.send(message)
