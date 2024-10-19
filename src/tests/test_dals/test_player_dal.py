from utilities import choose_from_list

from api.enums import PlayerStateEnum
from database.dals import PlayerDAL
from database.models.player import PlayerModel


async def test_get_player_by_id(
    players: list[list[PlayerModel]],
    player_dal: PlayerDAL,
):
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    fetched_player = await player_dal.get_player_by_id(player.id)
    assert fetched_player == player


async def test_ban_player_by_id(
    players: list[list[PlayerModel]],
    player_dal: PlayerDAL,
):
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    banned_player = await player_dal.ban_player_by_id(player.id)
    assert banned_player.state == PlayerStateEnum.banned
