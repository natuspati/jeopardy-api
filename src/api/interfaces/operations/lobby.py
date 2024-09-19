from typing import Annotated

from fastapi import Depends

from api.enums import PlayerStateEnum
from api.schemas.lobby import PaginatedLobbiesSchema
from api.schemas.nested.player import (
    LobbyWithPlayersInDBSchema,
    PlayerWithLobbyUserInDBSchema,
)
from api.schemas.player import PlayerInDBSchema
from api.schemas.query import DateTimeSchema, OrderSchema, PaginationSchema
from api.services import LobbyService, PlayerService
from api.services.pagination import PaginationService
from api.utilities import run_concurrently
from exceptions.http.authorization import (
    BannedPlayerStatusApiError,
    InsufficientPlayerStatusApiError,
)
from exceptions.http.lobby import PlayerLobbyDoesNotMatchApiError
from exceptions.http.not_found import NotFoundApiError


class LobbyOperationsInterface:
    def __init__(
        self,
        lobby_service: Annotated[LobbyService, Depends()],
        player_service: Annotated[PlayerService, Depends()],
        pagination_service: Annotated[PaginationService, Depends()],
    ):
        self._lobby_service = lobby_service
        self._player_service = player_service
        self._pagination = pagination_service

    async def get_lobbies(
        self,
        pagination: PaginationSchema,
        date: DateTimeSchema,
        order: OrderSchema,
    ) -> PaginatedLobbiesSchema:
        """
        Get lobbies.

        :param pagination: pagination parameters
        :param date: date filters
        :param order: order by filter
        :return: paginated list of lobbies
        """
        lobbies, lobby_count = await run_concurrently(
            self._lobby_service.get_lobbies(
                limit=pagination.page_size,
                offset=pagination.offset,
                start=date.start,
                end=date.end,
                order=order.order,
            ),
            self._lobby_service.total_count(),
        )
        self._pagination.configure(pagination)
        return self._pagination.paginate(
            total=lobby_count,
            items=lobbies,
            result_schema=PaginatedLobbiesSchema,
        )

    async def get_lobby(self, lobby_id: int) -> LobbyWithPlayersInDBSchema:
        """
        Get lobby with players associated with given lobby.

        :param lobby_id: lobby id
        :return: lobby with players
        """
        lobby = await self._lobby_service.get_lobby_by_id(lobby_id)
        if not lobby:
            raise NotFoundApiError()
        return lobby

    async def get_player(
        self,
        lobby_id: int,
        player_id: int,
    ) -> PlayerWithLobbyUserInDBSchema:
        """
        Get player information with associated user and lobby.

        :param lobby_id: lobby id
        :param player_id: player id
        :return: player with user and lobby data
        """
        player = await self._player_service.get_player_by_id(player_id)
        self._check_player_in_lobby(lobby_id=lobby_id, player=player)
        return player

    async def ban_player(
        self,
        lobby_id: int,
        lead_player: PlayerInDBSchema,
        player_id: int,
    ) -> PlayerInDBSchema:
        """
        Change player state to `banned`.

        :param lobby_id: lobby id
        :param lead_player: player with `lead` start in a lobby
        :param player_id: player id to ban
        :return: updated player
        """
        self._check_player_in_lobby(lobby_id=lobby_id, player=lead_player)
        self._check_player_is_lead(lead_player)
        return await self._player_service.ban_player_by_id(player_id)

    @classmethod
    def _check_player_in_lobby(cls, lobby_id: int, player: PlayerInDBSchema) -> None:
        if player.lobby_id != lobby_id:
            raise PlayerLobbyDoesNotMatchApiError()

    @classmethod
    def _check_player_is_lead(cls, player: PlayerInDBSchema) -> None:
        if player.state is not PlayerStateEnum.lead:
            raise InsufficientPlayerStatusApiError()

    @classmethod
    def _check_player_is_banned(cls, player: PlayerInDBSchema) -> None:
        if player.state is PlayerStateEnum.banned:
            raise BannedPlayerStatusApiError()
