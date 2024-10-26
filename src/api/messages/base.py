from abc import ABC

from api.enums.websocket import WebsocketMessageTypeEnum
from api.schemas.websocket import BaseWebsocketMessageSchema


class BaseWebsocketMessage(ABC):
    message_schema: type(BaseWebsocketMessageSchema) = BaseWebsocketMessageSchema
    message_type: WebsocketMessageTypeEnum
    message: str

    def __init__(self, **kwargs):
        self._schema = self.message_schema(
            message_type=self.message_type,
            message=self.message,
            **kwargs,
        )

    def to_dict(self):
        """
        Convert message to serializable dictionary.

        :return: serializable message
        """
        return self._schema.model_dump(mode="json")
