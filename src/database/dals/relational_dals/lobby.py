from datetime import datetime

from api.enums import OrderQueryEnum
from api.schemas.lobby import LobbyCreateSchema
from database.dals.relational_dals.base import BaseDAL
from database.models.lobby import LobbyModel
from database.query_managers import LobbyQueryManager


class LobbyDAL(BaseDAL):
    _qm = LobbyQueryManager

    async def get_lobbies(
        self,
        limit: int,
        offset: int | None = 0,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        order: OrderQueryEnum = OrderQueryEnum.desc,
    ) -> list[LobbyModel]:
        """
        Get lobbies.

        :param limit: max number of lobbies
        :param offset: offset
        :param start_date: start date
        :param end_date: end date
        :param order: order of lobbies in created_at column, descending by default
        :return: list of lobbies
        """
        return await self.select(
            where={"created_at": ("between", (start_date, end_date))},
            order={"created_at": order.value},
            many=True,
            limit=limit,
            offset=offset,
        )

    async def get_lobby_by_id(self, lobby_id: int) -> LobbyModel | None:
        """
        Get lobby by id.

        :param lobby_id: lobby id
        :return: lobby model or None
        """
        return await self.select(
            where={"id": lobby_id},
            related=["player_associations"],
        )

    async def create_lobby(self, lobby_create: LobbyCreateSchema) -> LobbyModel:
        """
        Create lobby.

        :param lobby_create: lobby create data
        :return: created lobby
        """
        return await self.insert(**lobby_create.model_dump())
