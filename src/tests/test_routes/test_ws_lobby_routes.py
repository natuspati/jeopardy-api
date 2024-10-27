import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from utilities import choose_from_list, create_auth_header

from api.enums.websocket import WebsocketMessageTypeEnum
from api.messages import LobbyConnectMessage
from database.models.player import PlayerModel
from database.models.user import UserModel


@pytest.mark.usefixtures("_reset_database")
async def test_join_lobby(
    users: dict[str, list[UserModel]],
    players: list[list[PlayerModel]],
    db_session: AsyncSession,
    http_client: TestClient,
):
    await db_session.commit()
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    user = next((user for user in users["active"] if user.id == player.user_id))
    url = http_client.app.url_path_for("join_lobby", lobby_id=player.lobby_id)
    connect_message = LobbyConnectMessage(player_id=player.id)
    with http_client.websocket_connect(
        url,
        headers=create_auth_header(user),
    ) as websocket:
        data = websocket.receive_json()
        assert data == connect_message.to_dict()

        user_message = "test"
        websocket.send_json({"message": "test"})
        data = websocket.receive_json()
        assert data["message"] == user_message
        assert data["message_type"] == WebsocketMessageTypeEnum.message.value
        assert data["sender"] == player.id
