from api.enums.websocket import WebsocketMessageTypeEnum
from api.schemas.base import BaseSchema


class BaseWebsocketMessageSchema(BaseSchema):
    message_type: WebsocketMessageTypeEnum
    message: str


class UserWebsocketMessageSchema(BaseWebsocketMessageSchema):
    sender: str | int
    receivers: list[str | int] | None = None
