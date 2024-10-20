from api.enums import PlayerStateEnum
from api.schemas.player import PlayerCreateSchema
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

    async def get_player_by_user_lobby(
        self,
        user_id: int,
        lobby_id: int,
    ) -> PlayerModel | None:
        """
        Get player by user and lobby ids.

        :param user_id: user id
        :param lobby_id: lobby id
        :return: player or None
        """
        return await self.select(
            where={"user_id": user_id, "lobby_id": lobby_id},
        )

    async def update_state_by_lobby_id(
        self,
        lobby_id: int,
        state: PlayerStateEnum,
    ) -> list[PlayerModel]:
        """
        Update player states in lobby.

        Players with state `lead` and `banned` cannot be updated.

        :param lobby_id:
        :param state:
        :return: list of updated players
        """
        return await self.update(
            where={
                "lobby_id": lobby_id,
                "state": ("not_in", (PlayerStateEnum.lead, PlayerStateEnum.banned)),
            },
            many=True,
            state=state,
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

    async def create_player(self, player_create: PlayerCreateSchema) -> PlayerModel:
        """
        Create player.

        :param player_create: player create data
        :return: created player
        """
        return await self.insert(**player_create.model_dump())
