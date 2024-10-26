from typing import Literal

from api.enums.websocket import WebsocketMessageTypeEnum
from api.schemas.base import BaseSchema


class BaseWebsocketMessageSchema(BaseSchema):
    message_type: WebsocketMessageTypeEnum
    message: str


class UserWebsocketMessageSchema(BaseWebsocketMessageSchema):
    sender: str | int
    receivers: Literal["all"] | list[str | int] = "all"
