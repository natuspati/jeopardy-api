from typing import Annotated

from fastapi import Depends, Header

from api.authnetication import decode_token, oauth2_scheme
from api.schemas.authnetication import UserInTokenSchema
from api.schemas.nested.user import UserWithLobbiesInDBSchema
from api.schemas.player import PlayerInDBSchema
from api.services import PlayerService, UserService
from exceptions.service.authorization import (
    InvalidCredentialsError,
    NotOwnerError,
    UserNotInLobby,
)
from exceptions.service.not_found import PlayerNotFoundError


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserInTokenSchema:
    """
    Get current user from OAuth 2 headers.

    :param token: token in headers
    :return: user data in the token
    """
    token_data = decode_token(token)
    if token_data.is_active is False:
        raise InvalidCredentialsError()
    return token_data


async def check_current_user(
    user_id: int,
    current_user: Annotated[UserInTokenSchema, Depends(get_current_user)],
) -> UserInTokenSchema:
    """
    Check current user has access to its resources.

    :param user_id: user id in path parameters
    :param current_user: current user
    :return: user that has access to the resources
    """
    if current_user.user_id != user_id:
        raise NotOwnerError()
    return current_user


async def check_current_user_in_lobby(
    lobby_id: int,
    current_user: Annotated[UserInTokenSchema, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends()],
) -> UserWithLobbiesInDBSchema:
    """
    Check if current user has a player in the lobby.

    :param lobby_id: lobby id
    :param current_user: current user
    :param user_service: user service
    :return: current user with lobbies and players
    """
    user_with_lobbies = await user_service.get_user_by_id(current_user.user_id)
    if not user_with_lobbies.has_lobby(lobby_id):
        raise UserNotInLobby()
    return user_with_lobbies


async def get_current_user_from_header(
    authorization: Annotated[str | None, Header()] = None,
) -> UserInTokenSchema:
    """
    Get current user from authorization header.

    :param authorization: authorization header
    :return: user in token
    """
    if authorization is None:
        raise InvalidCredentialsError()
    token = authorization.replace("Bearer ", "")
    return await get_current_user(token=token)


async def get_current_player(
    lobby_id: int,
    current_user: Annotated[UserInTokenSchema, Depends(get_current_user_from_header)],
    player_service: Annotated[PlayerService, Depends()],
) -> PlayerInDBSchema:
    """
    Get current player from authorization header.

    :param lobby_id: lobby id
    :param current_user: current user from header
    :param player_service: player service
    :return: player in database
    """
    player = await player_service.get_player_by_user_lobby(
        user_id=current_user.user_id,
        lobby_id=lobby_id,
    )
    if not player:
        raise PlayerNotFoundError()
    return player
