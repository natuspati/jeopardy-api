from typing import Annotated

from fastapi import Depends

from api.enums import PlayerStateEnum
from api.schemas.lobby import LobbyPlayerCreateSchema, PaginatedLobbiesSchema
from api.schemas.nested.player import (
    LobbyWithPlayersInDBSchema,
    PlayerWithLobbyUserInDBSchema,
)
from api.schemas.player import LobbyPlayerAddSchema, PlayerInDBSchema
from api.schemas.query import DateTimeSchema, OrderSchema, PaginationSchema
from api.services import LobbyService, PlayerService
from api.services.pagination import PaginationService
from api.utilities import run_concurrently
from exceptions.service.authorization import (
    BannedPlayerStatusError,
    InsufficientPlayerStatusError,
)
from exceptions.service.lobby import PlayerLobbyDoesNotMatchError
from exceptions.service.not_found import NotFoundError
from exceptions.service.resource import PlayerExistsError


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
            raise NotFoundError()
        return lobby

    async def create_lobby(
        self,
        user_id: int,
        lobby_player_create: LobbyPlayerCreateSchema,
    ) -> LobbyWithPlayersInDBSchema:
        """
        Create lobby and lead player.

        :param user_id: user that leads created lobby
        :param lobby_player_create: lobby and player create data
        :return: create lobby with lead player
        """
        lobby = await self._lobby_service.create_lobby(
            name=lobby_player_create.lobby_name,
        )
        await self._player_service.create_player(
            name=lobby_player_create.player_name,
            state=PlayerStateEnum.lead,
            lobby_id=lobby.id,
            user_id=user_id,
        )
        return await self.get_lobby(lobby_id=lobby.id)

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
        if not player:
            raise NotFoundError()
        await self._check_player_in_lobby(lobby_id=lobby_id, player=player)
        return player

    async def create_waiting_player(
        self,
        lobby_id: int,
        user_id: int,
        lobby_player_add: LobbyPlayerAddSchema,
    ) -> PlayerInDBSchema:
        """
        Add player with waiting state to a lobby.

        If player already exists and/or banned, raise error.

        :param lobby_id: lobby id
        :param user_id: user to add to the lobby
        :param lobby_player_add: player create data
        :return: created player
        """
        existing_player = await self._player_service.get_player_by_user_lobby(
            user_id=user_id,
            lobby_id=lobby_id,
        )
        if existing_player:
            await self._check_player_is_banned(existing_player)
            raise PlayerExistsError()

        return await self._player_service.create_player(
            name=lobby_player_add.name,
            state=PlayerStateEnum.waiting,
            lobby_id=lobby_id,
            user_id=user_id,
        )

    async def start_lobby(self, lobby_id: int) -> LobbyWithPlayersInDBSchema:
        """
        Start lobby.

        :param lobby_id: lobby id
        :return: lobby with players in `playing` state.
        """
        await self._player_service.update_state_by_lobby_id(
            lobby_id=lobby_id,
            state=PlayerStateEnum.playing,
        )
        return await self.get_lobby(lobby_id=lobby_id)

    async def ban_player(
        self,
        lobby_id: int,
        lead_player_id: int,
        player_id: int,
    ) -> PlayerInDBSchema:
        """
        Change player state to `banned`.

        :param lobby_id: lobby id
        :param lead_player_id: player id with `lead` state in the lobby
        :param player_id: player id to ban
        :return: updated player
        """
        await self._check_player_in_lobby(lobby_id=lobby_id, player=player_id)
        await self._check_player_is_lead(lead_player_id)
        return await self._player_service.ban_player_by_id(player_id)

    async def _check_player_in_lobby(
        self,
        lobby_id: int,
        player: PlayerInDBSchema | int,
    ) -> None:
        if isinstance(player, int):
            player = await self._player_service.get_player_by_id(player)
        if player.lobby_id != lobby_id:
            raise PlayerLobbyDoesNotMatchError()

    async def _check_player_is_lead(
        self,
        player: PlayerInDBSchema | int,
    ) -> None:
        if isinstance(player, int):
            player = await self._player_service.get_player_by_id(player)
        if player.state is not PlayerStateEnum.lead:
            raise InsufficientPlayerStatusError()

    async def _check_player_is_banned(
        self,
        player: PlayerInDBSchema | int,
    ) -> None:
        if isinstance(player, int):
            player = await self._player_service.get_player_by_id(player)
        if player.state is PlayerStateEnum.banned:
            raise BannedPlayerStatusError()
