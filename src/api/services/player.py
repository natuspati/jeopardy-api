from typing import Annotated

from fastapi import Depends

from api.schemas.nested.player import PlayerWithLobbyUserInDBSchema
from api.schemas.player import PlayerInDBSchema
from api.services.mixins import DBModelValidatorMixin
from database.dals import PlayerDAL


class PlayerService(DBModelValidatorMixin):
    def __init__(
        self,
        player_dal: Annotated[PlayerDAL, Depends()],
    ):
        self._player_dal = player_dal

    async def get_player_by_id(self, player_id: int) -> PlayerWithLobbyUserInDBSchema:
        """
        Get player by id with associated lobbies.

        :param player_id: player id
        :return: player with associated lobbies
        """
        player_in_db = await self._player_dal.get_player_by_id(player_id)
        return self.validate(player_in_db, PlayerWithLobbyUserInDBSchema)

    async def ban_player_by_id(self, player_id: int) -> PlayerInDBSchema:
        """
        Set player state to `banned`.

        :param player_id: player id
        :return: banned player
        """
        player_in_db = await self._player_dal.ban_player_by_id(player_id)
        return self.validate(player_in_db, PlayerInDBSchema)
