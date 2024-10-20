from fastapi import status

from exceptions.service.base import BaseServiceError


class PlayerError(BaseServiceError):
    detail = "Operation on Player API failed"
    status_code = status.HTTP_400_BAD_REQUEST


class UpdatePlayerStateInvalidError(PlayerError):
    detail = "Update on player state is invalid"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
