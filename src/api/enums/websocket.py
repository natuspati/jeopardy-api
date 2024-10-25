from enum import Enum


class WebsocketMessageTypeEnum(Enum):
    connect = "connect"
    disconnect = "disconnect"
    message = "message"
    error = "error"
