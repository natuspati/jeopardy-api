from typing import Any

from exceptions.service.base import BaseError


class SerializationError(BaseError):
    detail = "Serialization error"


class NonSerializableError(SerializationError):
    detail = "Object can not be serialized"


class JSONEncoderError(SerializationError):
    detail = "Object {encoded_value} cannot be serialized by JSON encoder"

    def __init__(self, encoded_value: Any):
        super().__init__(detail=self.detail.format(encoded_value=encoded_value))


class JSONDecoderError(SerializationError):
    detail = "Object {decoded_value} cannot be deserialized by JSON decoder"

    def __init__(self, decoded_value: Any):
        super().__init__(detail=self.detail.format(decoded_value=decoded_value))
