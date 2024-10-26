from fastapi import status

from exceptions.service.base import BaseServiceError


class MessageError(BaseServiceError):
    detail = "Message error"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    ws_status_code = status.WS_1003_UNSUPPORTED_DATA


class InvalidMessageTypeError(MessageError):
    def __init__(self, message_type: str):
        detail = f"Invalid message type: {message_type}"
        super().__init__(detail)
