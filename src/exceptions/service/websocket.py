from exceptions.service.base import BaseServiceError


class BaseWebsocketError(BaseServiceError):
    pass


class WebsocketInvalidStateError(BaseWebsocketError):
    detail = "Websocket state is invalid"


class WebsocketRoomExistsError(BaseWebsocketError):
    detail = "Room already exists"


class WebsocketRoomNotExistsError(BaseWebsocketError):
    detail = "Room does not exist"


class WebsocketConnectionExistsError(BaseWebsocketError):
    detail = "Connection already exists"


class WebsocketConnectionNotExistsError(BaseWebsocketError):
    detail = "Connection does not exists"
