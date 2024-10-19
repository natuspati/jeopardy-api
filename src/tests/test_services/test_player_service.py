from utilities import choose_from_list

from api.enums import PlayerStateEnum
from api.services import PlayerService
from database.models.player import PlayerModel


async def test_get_player_by_id(
    players: list[list[PlayerModel]],
    player_service: PlayerService,
):
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    fetched_player = await player_service.get_player_by_id(player.id)
    assert fetched_player.model_dump() == player.to_dict(include_related=True)


async def test_ban_player_by_id(
    players: list[list[PlayerModel]],
    player_service: PlayerService,
):
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    banned_player = await player_service.ban_player_by_id(player.id)
    assert banned_player.state == PlayerStateEnum.banned
