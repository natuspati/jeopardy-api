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
        receivers: list[str | int] | None = None,
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

    def to_dict(self) -> dict:
        """
        Convert user message to serializable dictionary without receivers field.

        :return: user message
        """
        return super().to_dict(exclude={"receivers"})
