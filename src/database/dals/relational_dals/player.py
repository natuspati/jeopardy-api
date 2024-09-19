from api.enums import PlayerStateEnum
from database.dals.relational_dals.base import BaseDAL
from database.models.player import PlayerModel
from database.query_managers import PlayerQueryManager


class PlayerDAL(BaseDAL):
    _qm = PlayerQueryManager

    async def get_player_by_id(self, player_id: int) -> PlayerModel | None:
        """
        Get player by id.

        :param player_id: player id
        :return: player or None
        """
        return await self.select(
            where={"id": player_id},
            related=["lobby", "user"],
        )

    async def ban_player_by_id(self, player_id: int) -> PlayerModel:
        """
        Change player state to banned.

        :param player_id: player id to ban
        :return: banned player
        """
        return await self.update(
            where={"id": player_id},
            state=PlayerStateEnum.banned,
        )
