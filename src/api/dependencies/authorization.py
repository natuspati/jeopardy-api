from typing import Annotated

from fastapi import Depends

from api.authnetication import decode_token, oauth2_scheme
from api.schemas.nested.user import UserWithLobbiesInDBSchema
from api.schemas.user import UserInDBSchema
from api.services import UserService
from exceptions.service.authorization import (
    InvalidCredentialsError,
    NotOwnerError,
    UserNotInLobby,
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: Annotated[UserService, Depends()],
) -> UserInDBSchema:
    """
    Get current user from OAuth 2 headers.

    :param token: token in headers
    :param user_service: user service
    :return: user in database
    """
    token_data = decode_token(token)
    user = await user_service.get_user_by_username(token_data.username)
    if user is None or user.is_active is False:
        raise InvalidCredentialsError()
    return user


async def check_current_user(
    user_id: int,
    current_user: Annotated[UserInDBSchema, Depends(get_current_user)],
) -> UserInDBSchema:
    """
    Check current user has access to its resources.

    :param user_id: user id in path parameters
    :param current_user: current user
    :return:
    """
    if current_user.id != user_id:
        raise NotOwnerError()
    return current_user


async def check_current_user_in_lobby(
    lobby_id: int,
    current_user: Annotated[UserInDBSchema, Depends(get_current_user)],
    user_service: Annotated[UserService, Depends()],
) -> UserWithLobbiesInDBSchema:
    """
    Check if current user has a player in the lobby.

    :param lobby_id: lobby id
    :param current_user: current user
    :param user_service: user service
    :return: current user with lobbies and players
    """
    user_with_lobbies = await user_service.get_user_by_id(current_user.id)
    if not user_with_lobbies.has_lobby(lobby_id):
        raise UserNotInLobby()
    return user_with_lobbies
