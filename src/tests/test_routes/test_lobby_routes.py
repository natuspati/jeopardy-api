import pytest
from factories.lobby import LobbyPlayerCreateFactory
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from utilities import choose_from_list, create_auth_header

from api.enums import PlayerStateEnum
from database.models.lobby import LobbyModel
from database.models.player import PlayerModel
from database.models.user import UserModel


@pytest.mark.usefixtures("_reset_database")
async def test_get_lobbies(
    lobbies: list[LobbyModel],
    db_session: AsyncSession,
    auth_client: TestClient,
):
    await db_session.commit()
    url = auth_client.app.url_path_for("get_lobbies")
    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    fetched_lobbies = response.json()["items"]
    assert len(lobbies) == len(fetched_lobbies)


@pytest.mark.usefixtures("_reset_database")
async def test_get_lobby(
    users: dict[str, list[UserModel]],
    lobbies: list[LobbyModel],
    players: list[list[PlayerModel]],
    db_session: AsyncSession,
    http_client: TestClient,
):
    await db_session.commit()
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    lobby = next((lobby for lobby in lobbies if lobby.id == player.lobby_id))
    user = next((user for user in users["active"] if user.id == player.user_id))
    url = http_client.app.url_path_for("get_lobby", lobby_id=player.lobby_id)
    response = http_client.get(url, headers=create_auth_header(user))
    assert response.status_code == status.HTTP_200_OK

    fetched_lobby = response.json()
    fetched_players = fetched_lobby.pop("players")
    fetched_join_link = fetched_lobby.pop("join_url")
    players_as_dict = [player.to_dict(to_string=True) for player in players_in_lobby]
    assert fetched_lobby == lobby.to_dict(to_string=True)
    assert fetched_players == players_as_dict
    assert fetched_join_link == http_client.app.url_path_for(
        "join_lobby",
        lobby_id=player.lobby_id,
    )


@pytest.mark.usefixtures("_reset_database")
async def test_create_lobby(
    users: dict[str, list[UserModel]],
    db_session: AsyncSession,
    http_client: TestClient,
):
    await db_session.commit()
    user = choose_from_list(users["active"])
    lobby_create = LobbyPlayerCreateFactory.build()
    url = http_client.app.url_path_for("create_lobby")
    response = http_client.post(
        url,
        json=lobby_create.model_dump(),
        headers=create_auth_header(user),
    )
    assert response.status_code == status.HTTP_201_CREATED

    created_lobby = response.json()
    assert created_lobby["name"] == lobby_create.lobby_name
    assert len(created_lobby["players"]) == 1
    created_player = created_lobby["players"][0]
    assert created_player["name"] == lobby_create.player_name
    assert created_player["user_id"] == user.id
    assert created_player["state"] == PlayerStateEnum.lead.value
