from api.enums.websocket import WebsocketMessageTypeEnum
from api.messages.base import BaseWebsocketMessage


class LobbyConnectMessage(BaseWebsocketMessage):
    message_type = WebsocketMessageTypeEnum.connect

    def __init__(self, player_id: int):
        self.message = f"Player {player_id} joined the lobby."
        super().__init__()


class LobbyDisconnectMessage(BaseWebsocketMessage):
    message_type = WebsocketMessageTypeEnum.disconnect

    def __init__(self, player_id: int):
        self.message = f"Player {player_id} left the lobby."
        super().__init__()
