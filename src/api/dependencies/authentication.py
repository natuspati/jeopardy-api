from typing import Annotated

from fastapi import Depends

from api.authnetication import decode_token, oauth2_scheme
from api.schemas.user import UserInDBSchema
from api.services import UserService
from exceptions.http.authorization import InvalidCredentialsApiError


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
        raise InvalidCredentialsApiError()
    return user
