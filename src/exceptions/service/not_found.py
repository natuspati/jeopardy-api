from fastapi import status

from exceptions.service.base import BaseServiceError


class NotFoundError(BaseServiceError):
    detail = "Resource not found."
    status_code = status.HTTP_404_NOT_FOUND
    ws_status_code = status.WS_1003_UNSUPPORTED_DATA


class PlayerNotFoundError(BaseServiceError):
    detail = "Player not found."
