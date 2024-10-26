from typing import Annotated

from fastapi import Depends
from pydantic import ValidationError

from api.enums import PlayerStateEnum
from api.schemas.nested.player import PlayerWithLobbyUserInDBSchema
from api.schemas.player import PlayerCreateSchema, PlayerInDBSchema
from api.services.mixins import DBModelValidatorMixin
from cutom_types.player import UPDATE_PLAYER_STATE_TYPE
from database.dals import PlayerDAL
from exceptions.service.player import UpdatePlayerStateInvalidError
from exceptions.service.schema import SchemaValidationError


class PlayerService(DBModelValidatorMixin):
    def __init__(
        self,
        player_dal: Annotated[PlayerDAL, Depends()],
    ):
        self._player_dal = player_dal

    async def get_player_by_id(
        self,
        player_id: int,
    ) -> PlayerWithLobbyUserInDBSchema | None:
        """
        Get player by id with associated lobbies.

        :param player_id: player id
        :return: player with associated lobbies
        """
        player_in_db = await self._player_dal.get_player_by_id(player_id)
        return self.validate(player_in_db, PlayerWithLobbyUserInDBSchema)

    async def get_player_by_user_lobby(
        self,
        user_id: int,
        lobby_id: int,
    ) -> PlayerInDBSchema | None:
        """
        Get player by user and lobby ids.

        :param user_id: user id
        :param lobby_id: lobby id
        :return: player or None
        """
        player_in_db = await self._player_dal.get_player_by_user_lobby(
            user_id=user_id,
            lobby_id=lobby_id,
        )
        return self.validate(player_in_db, PlayerInDBSchema)

    async def update_state_by_lobby_id(
        self,
        lobby_id: int,
        state: UPDATE_PLAYER_STATE_TYPE,
    ) -> list[PlayerInDBSchema]:
        """
        Update player states in a lobby.

        State can only be `waiting`, `playing` or `inactive`.

        `lead` and `banned` players are unaffected.

        :param lobby_id: lobby id
        :param state: player state to update to
        :return: updated players
        """
        valid_states = (
            PlayerStateEnum.waiting,
            PlayerStateEnum.playing,
            PlayerStateEnum.inactive,
        )
        if state in valid_states:
            updated_players = await self._player_dal.update_state_by_lobby_id(
                lobby_id=lobby_id,
                state=state,
            )
        else:
            raise UpdatePlayerStateInvalidError()
        return self.validate(updated_players, PlayerInDBSchema)

    async def ban_player_by_id(self, player_id: int) -> PlayerInDBSchema:
        """
        Set player state to `banned`.

        :param player_id: player id
        :return: banned player
        """
        player_in_db = await self._player_dal.ban_player_by_id(player_id)
        return self.validate(player_in_db, PlayerInDBSchema)

    async def create_player(
        self,
        name: str,
        state: PlayerStateEnum,
        lobby_id: int,
        user_id: int,
    ) -> PlayerInDBSchema:
        """
        Create player.

        :param name: player name
        :param state: player state
        :param lobby_id: lobby id
        :param user_id: user id
        :return: created player
        """
        try:
            player_create = PlayerCreateSchema(
                name=name,
                state=state,
                lobby_id=lobby_id,
                user_id=user_id,
            )
        except ValidationError as error:
            raise SchemaValidationError(error) from error
        player = await self._player_dal.create_player(player_create)
        return self.validate(player, PlayerInDBSchema)
