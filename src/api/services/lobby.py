from datetime import datetime
from typing import Annotated

from fastapi import Depends
from pydantic import ValidationError

from api.enums.query import OrderQueryEnum
from api.schemas.lobby import LobbyCreateSchema, LobbyInDBSchema
from api.schemas.nested.player import LobbyWithPlayersSchema
from api.services.mixins import DBModelValidatorMixin
from database.dals.relational_dals.lobby import LobbyDAL
from exceptions.service.schema import SchemaValidationError


class LobbyService(DBModelValidatorMixin):
    def __init__(
        self,
        lobby_dal: Annotated[LobbyDAL, Depends()],
    ):
        self._lobby_dal = lobby_dal

    async def get_lobbies(
        self,
        limit: int,
        offset: int = 0,
        start: datetime | None = None,
        end: datetime | None = None,
        order: OrderQueryEnum = OrderQueryEnum.desc,
    ) -> list[LobbyInDBSchema]:
        """
        Get lobbies.

        :param limit: limit of lobbies to fetch
        :param offset: offset
        :param start: start date
        :param end: end date
        :param order: order of lobbies by create_at field, descending by default
        :return: lobbies
        """
        lobbies_in_db = await self._lobby_dal.get_lobbies(
            limit=limit,
            offset=offset,
            start_date=start,
            end_date=end,
            order=order,
        )
        return self.validate(lobbies_in_db, LobbyInDBSchema)

    async def get_lobby_by_id(self, lobby_id: int) -> LobbyWithPlayersSchema | None:
        """
        Get lobby by id.

        :param lobby_id: lobby id
        :return: lobby with associated players
        """
        lobby_in_db = await self._lobby_dal.get_lobby_by_id(lobby_id=lobby_id)
        return self.validate(lobby_in_db, LobbyWithPlayersSchema)

    async def create_lobby(self, name: str) -> LobbyInDBSchema:
        """
        Create lobby.

        :param name: str
        :return: created lobby
        """
        try:
            lobby_create = LobbyCreateSchema(name=name)
        except ValidationError as error:
            raise SchemaValidationError(error) from error
        lobby = await self._lobby_dal.create_lobby(lobby_create)
        return self.validate(lobby, LobbyInDBSchema)

    async def total_count(self) -> int:
        """
        Get total number of lobbies.

        :return: total number of lobbies
        """
        return await self._lobby_dal.total_count()
