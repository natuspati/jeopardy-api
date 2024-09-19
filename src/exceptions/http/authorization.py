from fastapi import status

from exceptions.http.base import BaseApiError


class UnauthorizedApiError(BaseApiError):
    detail = "Unauthorized"
    status_code = status.HTTP_401_UNAUTHORIZED


class InvalidTokenApiError(UnauthorizedApiError):
    detail = "Invalid token"


class InvalidCredentialsApiError(UnauthorizedApiError):
    detail = "Invalid credentials"


class InsufficientPlayerStatusApiError(UnauthorizedApiError):
    detail = "Player status must be lead."


class BannedPlayerStatusApiError(UnauthorizedApiError):
    detail = "Player status must not be banned."
