from datetime import timedelta

import pytest
from factories.token import TokenDataFactory
from utilities import choose_from_list

from api.authnetication import create_access_token
from api.dependencies import get_current_user
from api.dependencies.authorization import (
    check_current_user,
    check_current_user_in_lobby,
)
from api.schemas.authnetication import TokenDataSchema
from api.services import UserService
from database.models.player import PlayerModel
from database.models.user import UserModel
from exceptions.service.authorization import (
    InvalidCredentialsError,
    InvalidTokenError,
    NotOwnerError,
    UserNotInLobby,
)


async def test_get_current_user(
    active_user: UserModel,
    user_service: UserService,
):
    token_data = TokenDataSchema(user_id=active_user.id, sub=active_user.username)
    access_token = create_access_token(
        data=token_data.model_dump(by_alias=True),
    )
    current_user = await get_current_user(token=access_token, user_service=user_service)
    assert current_user.model_dump() == active_user.to_dict()


async def test_get_current_user_fails_if_inactive(
    inactive_user: UserModel,
    user_service: UserService,
):
    token_data = TokenDataSchema(user_id=inactive_user.id, sub=inactive_user.username)
    access_token = create_access_token(
        data=token_data.model_dump(by_alias=True),
    )
    with pytest.raises(InvalidCredentialsError):
        await get_current_user(token=access_token, user_service=user_service)


async def test_get_current_user_fails_if_invalid_token(
    user_service: UserService,
):
    access_token_expires = timedelta(seconds=-1)
    token_data: TokenDataSchema = TokenDataFactory.build()
    access_token = create_access_token(
        data=token_data.model_dump(by_alias=True),
        expires_delta=access_token_expires,
    )
    with pytest.raises(InvalidTokenError):
        await get_current_user(token=access_token, user_service=user_service)


async def test_check_current_user(
    active_user: UserModel,
    user_service: UserService,
):
    user = await user_service.get_user_by_username(active_user.username)
    current_user = await check_current_user(user_id=user.id, current_user=user)
    assert current_user == user
    with pytest.raises(NotOwnerError):
        await check_current_user(user_id=user.id + 1, current_user=user)


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
    current_user = await user_service.get_user_by_username(selected_user.username)
    user = await check_current_user_in_lobby(
        lobby_id=player_in_lobby.lobby_id,
        current_user=current_user,
        user_service=user_service,
    )
    assert user.id == current_user.id
    assert user.has_lobby(player_in_lobby.lobby_id)

    users_ids_in_lobby = [player.user_id for player in players_in_lobby]
    user_not_in_lobby = next(
        (user for user in users["active"] if user.id not in users_ids_in_lobby),
        None,
    )
    if not user_not_in_lobby:
        pytest.fail("User must exist in database that is not in the lobby")
    current_user_not_in_lobby = await user_service.get_user_by_username(
        username=user_not_in_lobby.username,
    )
    with pytest.raises(UserNotInLobby):
        await check_current_user_in_lobby(
            lobby_id=player_in_lobby.lobby_id,
            current_user=current_user_not_in_lobby,
            user_service=user_service,
        )
