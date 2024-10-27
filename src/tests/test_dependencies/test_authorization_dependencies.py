from datetime import timedelta

import pytest
from factories.token import UserTokenFactory
from factories.user import UserInTokenFactory
from utilities import choose_from_list

from api.authnetication import create_access_token
from api.dependencies import (
    check_current_user,
    check_current_user_in_lobby,
    get_current_player,
    get_current_user,
    get_current_user_from_header,
)
from api.schemas.authnetication import UserInTokenSchema
from api.services import PlayerService, UserService
from database.models.player import PlayerModel
from database.models.user import UserModel
from exceptions.service.authorization import (
    InvalidCredentialsError,
    InvalidTokenError,
    NotOwnerError,
    UserNotInLobby,
)
from exceptions.service.not_found import PlayerNotFoundError


async def test_get_current_user(active_user: UserModel):
    token_data = UserInTokenSchema(
        user_id=active_user.id,
        sub=active_user.username,
        is_active=True,
    )
    access_token = create_access_token(
        data=token_data.model_dump(by_alias=True),
    )
    current_user = await get_current_user(token=access_token)
    assert current_user.username == active_user.username
    assert current_user.user_id == active_user.id
    assert current_user.is_active == active_user.is_active


async def test_get_current_user_fails_if_inactive(
    inactive_user: UserModel,
    user_service: UserService,
):
    token_data = UserInTokenSchema(
        user_id=inactive_user.id,
        sub=inactive_user.username,
        is_active=False,
    )
    access_token = create_access_token(
        data=token_data.model_dump(by_alias=True),
    )
    with pytest.raises(InvalidCredentialsError):
        await get_current_user(token=access_token)


async def test_get_current_user_fails_if_invalid_token():
    access_token_expires = timedelta(seconds=-1)
    token_data: UserInTokenSchema = UserTokenFactory.build()
    access_token = create_access_token(
        data=token_data.model_dump(by_alias=True),
        expires_delta=access_token_expires,
    )
    with pytest.raises(InvalidTokenError):
        await get_current_user(token=access_token)


async def test_check_current_user():
    user = UserInTokenFactory.build()
    current_user = await check_current_user(user_id=user.user_id, current_user=user)
    assert current_user == user
    with pytest.raises(NotOwnerError):
        await check_current_user(user_id=user.user_id + 1, current_user=user)


async def test_check_current_user_in_lobby(
    users: dict[str, list[UserModel]],
    players: list[list[PlayerModel]],
    user_service: UserService,
):
    players_in_lobby = choose_from_list(players)
    player_in_lobby = choose_from_list(players_in_lobby)
    selected_user = next(
        (user for user in users["active"] if user.id == player_in_lobby.user_id),
        None,
    )
    if not selected_user:
        pytest.fail("User must exist in database that is in the lobby")
    current_user = UserInTokenFactory.build(
        user_id=selected_user.id,
        username=selected_user.username,
    )
    user = await check_current_user_in_lobby(
        lobby_id=player_in_lobby.lobby_id,
        current_user=current_user,
        user_service=user_service,
    )
    assert user.id == current_user.user_id
    assert user.has_lobby(player_in_lobby.lobby_id)

    users_ids_in_lobby = [player.user_id for player in players_in_lobby]
    user_not_in_lobby = next(
        (user for user in users["active"] if user.id not in users_ids_in_lobby),
        None,
    )
    if not user_not_in_lobby:
        pytest.fail("User must exist in database that is not in the lobby")
    current_user_not_in_lobby = UserInTokenFactory.build(
        user_id=user_not_in_lobby.id,
        username=user_not_in_lobby.username,
    )
    with pytest.raises(UserNotInLobby):
        await check_current_user_in_lobby(
            lobby_id=player_in_lobby.lobby_id,
            current_user=current_user_not_in_lobby,
            user_service=user_service,
        )


async def test_get_current_user_from_header(active_user: UserModel):
    token_data = UserInTokenSchema(
        user_id=active_user.id,
        sub=active_user.username,
        is_active=True,
    )
    access_token = create_access_token(
        data=token_data.model_dump(by_alias=True),
    )
    current_user = await get_current_user_from_header(
        authorization=f"Bearer {access_token}",
    )
    assert current_user.username == active_user.username
    assert current_user.user_id == active_user.id
    assert current_user.is_active == active_user.is_active


async def test_get_current_player(
    users: dict[str, list[UserModel]],
    players: list[list[PlayerModel]],
    player_service: PlayerService,
):
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    user = next((user for user in users["active"] if user.id == player.user_id))
    token_data = UserInTokenSchema(
        user_id=user.id,
        sub=user.username,
        is_active=True,
    )
    player_in_db = await get_current_player(
        lobby_id=player.lobby_id,
        current_user=token_data,
        player_service=player_service,
    )
    assert player_in_db.model_dump() == player.to_dict()

    users_ids_in_lobby = [player.user_id for player in players_in_lobby]
    user_not_in_lobby = next(
        (user for user in users["active"] if user.id not in users_ids_in_lobby),
        None,
    )
    if not user_not_in_lobby:
        pytest.fail("User must exist in database that is not in the lobby")
    current_user_not_in_lobby = UserInTokenFactory.build(
        user_id=user_not_in_lobby.id,
        username=user_not_in_lobby.username,
    )
    with pytest.raises(PlayerNotFoundError):
        await get_current_player(
            lobby_id=player.lobby_id,
            current_user=current_user_not_in_lobby,
            player_service=player_service,
        )
