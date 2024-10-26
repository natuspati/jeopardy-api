from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pydantic import ValidationError

from api.schemas.authnetication import UserInTokenSchema
from exceptions.service.authorization import InvalidTokenError
from settings import settings


def decode_token(token: str) -> UserInTokenSchema:
    """
    Decode a JWT token.

    :param token: encoded JWT token
    :return: decoded JWT token payload
    """
    try:
        payload: dict[str, Any] = jwt.decode(
            jwt=token,
            key=settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except jwt.InvalidTokenError:
        raise InvalidTokenError()

    try:
        return UserInTokenSchema.model_validate(payload)
    except ValidationError:
        raise InvalidTokenError()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    If expiration time is not provided, current time + value from settings is used.

    :param data: data to insert into payload
    :param expires_delta: expiration time from current time
    :return: encoded JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_min,
        )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )
