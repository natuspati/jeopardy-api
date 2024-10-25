from api.enums.websocket import WebsocketMessageTypeEnum
from api.schemas.base import BaseSchema


class BaseWebsocketMessageSchema(BaseSchema):
    type: WebsocketMessageTypeEnum
    message: str
