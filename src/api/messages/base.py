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

    def to_dict(self, exclude: set[str] | None = None):
        """
        Convert message to serializable dictionary.

        :param exclude: fields to exclude
        :return: serializable message
        """
        return self._schema.model_dump(mode="json", exclude=exclude)
