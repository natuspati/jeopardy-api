from fastapi import status

from exceptions.service.base import BaseServiceError


class UnauthorizedError(BaseServiceError):
    detail = "Unauthorized"
    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenError(BaseServiceError):
    detail = "Forbidden"
    status_code = status.HTTP_403_FORBIDDEN


class InvalidTokenError(UnauthorizedError):
    detail = "Invalid token"


class InvalidCredentialsError(UnauthorizedError):
    detail = "Invalid credentials"


class InsufficientPlayerStatusError(UnauthorizedError):
    detail = "Player status must be lead."


class BannedPlayerStatusError(ForbiddenError):
    detail = "Player status must not be banned."


class NotOwnerError(ForbiddenError):
    detail = "Request user does not own the resource"


class UserNotInLobby(ForbiddenError):
    detail = "User is not in lobby."
