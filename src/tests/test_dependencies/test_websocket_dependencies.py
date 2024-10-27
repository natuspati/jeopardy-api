from unittest.mock import AsyncMock

from fastapi import WebSocket
from starlette.websockets import WebSocketState
from utilities import choose_from_list

from api.dependencies import get_lobby_connection, get_lobby_room
from api.services import ConnectionManager, PlayerService
from database.models.player import PlayerModel


async def test_get_lobby_room(
    lobby_raw_data: tuple[dict, dict, dict],
    ws_conn_manager: ConnectionManager,
):
    first_lobby = lobby_raw_data[0]
    room = await get_lobby_room(
        lobby_id=first_lobby["id"],
        conn_manager=ws_conn_manager,
    )
    assert room.id == first_lobby["id"]


async def test_get_lobby_connection(
    players: list[list[PlayerModel]],
    ws_conn_manager: ConnectionManager,
    player_service: PlayerService,
):
    players_in_lobby = choose_from_list(players)
    player_in_lobby = choose_from_list(players_in_lobby)
    player = await player_service.get_player_by_user_lobby(
        user_id=player_in_lobby.user_id,
        lobby_id=player_in_lobby.lobby_id,
    )
    lobby_room = ws_conn_manager.get_or_create_room(room_id=player.lobby_id)
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.client_state = WebSocketState.CONNECTED
    async for connection in get_lobby_connection(  # noqa: WPS352
        lobby_room=lobby_room,
        current_player=player,
        conn_manager=ws_conn_manager,
        websocket=mock_websocket,
    ):
        assert connection.id == player.id
