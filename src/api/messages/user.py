from typing import Literal

from api.enums.websocket import WebsocketMessageTypeEnum
from api.messages.base import BaseWebsocketMessage
from api.schemas.websocket import UserWebsocketMessageSchema
from exceptions.service.message import InvalidMessageTypeError


class UserMessage(BaseWebsocketMessage):
    message_schema = UserWebsocketMessageSchema
    message_type = WebsocketMessageTypeEnum.message

    def __init__(
        self,
        message: str,
        sender: str | int,
        receivers: Literal["all"] | list[str] = "all",
        message_type: str | None = None,
    ):
        if message_type:
            try:
                self.message_type = WebsocketMessageTypeEnum(  # noqa: WPS601
                    message_type,
                )
            except ValueError:
                raise InvalidMessageTypeError(message_type)
        self.message = message
        self.sender = sender
        self.receivers = receivers
        super().__init__(sender=sender, receivers=receivers)
