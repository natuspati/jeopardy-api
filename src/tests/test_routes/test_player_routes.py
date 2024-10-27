import pytest
from factories.lobby import LobbyPlayerAddFactory
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from utilities import choose_from_list, create_auth_header

from api.enums import PlayerStateEnum
from database.models.lobby import LobbyModel
from database.models.player import PlayerModel
from database.models.user import UserModel


@pytest.mark.usefixtures("_reset_database")
async def test_get_player(
    users: dict[str, list[UserModel]],
    players: list[list[PlayerModel]],
    db_session: AsyncSession,
    http_client: TestClient,
    fastapi_app: FastAPI,
):
    await db_session.commit()
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    user = next((user for user in users["active"] if user.id == player.user_id))
    url = http_client.app.url_path_for(
        "get_player",
        lobby_id=player.lobby_id,
        player_id=player.id,
    )
    response = http_client.get(url, headers=create_auth_header(user))
    assert response.status_code == status.HTTP_200_OK

    fetched_player = response.json()
    join_link = fetched_player.pop("join_url")
    player_as_dict = player.to_dict(include_related=True, to_string=True)
    player_as_dict["user"].pop("password")
    player_as_dict["user"].pop("is_active")
    assert fetched_player == player_as_dict
    assert join_link == fastapi_app.url_path_for("join_lobby", lobby_id=player.lobby_id)


@pytest.mark.usefixtures("_reset_database")
async def test_create_player(
    active_user: UserModel,
    lobbies: list[LobbyModel],
    db_session: AsyncSession,
    http_client: TestClient,
):
    await db_session.commit()
    lobby = choose_from_list(lobbies)
    player_add = LobbyPlayerAddFactory.build()
    url = http_client.app.url_path_for("create_player", lobby_id=lobby.id)
    response = http_client.post(
        url,
        json=player_add.model_dump(),
        headers=create_auth_header(active_user),
    )
    assert response.status_code == status.HTTP_201_CREATED

    created_player = response.json()
    assert created_player["name"] == player_add.name
    assert created_player["state"] == PlayerStateEnum.waiting.value
    assert created_player["lobby_id"] == lobby.id
    assert created_player["user_id"] == active_user.id
