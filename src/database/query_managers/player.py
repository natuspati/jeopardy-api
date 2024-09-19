from database.models.lobby import LobbyModel
from database.models.player import PlayerModel
from database.models.user import UserModel
from database.query_managers.base import BaseQueryManager


class PlayerQueryManager(BaseQueryManager):
    _model = PlayerModel
    _association_models = {
        "lobby": {
            "model": LobbyModel,
            "on": LobbyModel.id == PlayerModel.lobby_id,
            "isouter": False,
        },
        "user": {
            "model": UserModel,
            "on": UserModel.id == PlayerModel.lobby_id,
            "isouter": False,
        },
    }
