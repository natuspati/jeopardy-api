from database.models.lobby import LobbyModel
from database.models.player import PlayerModel
from database.query_managers.base import BaseQueryManager


class LobbyQueryManager(BaseQueryManager):
    _model = LobbyModel
    _association_models = {
        "player": {
            "model": PlayerModel,
            "on": LobbyModel.id == PlayerModel.lobby_id,
            "isouter": False,
        },
    }
