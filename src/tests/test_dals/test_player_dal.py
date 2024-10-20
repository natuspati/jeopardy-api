import pytest
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


async def test_update_state_by_lobby_id(
    players: list[list[PlayerModel]],
    player_dal: PlayerDAL,
):
    lobby_id = 3
    players_in_waiting_lobby = players[lobby_id - 1]
    waiting_players = [
        player
        for player in players_in_waiting_lobby
        if player.state == PlayerStateEnum.waiting
    ]
    if not waiting_players:
        pytest.fail("Third lobby must have waiting players")
    playing_players = await player_dal.update_state_by_lobby_id(
        lobby_id=lobby_id,
        state=PlayerStateEnum.playing,
    )
    assert len(waiting_players) == len(playing_players)
    for playing_player in playing_players:
        assert playing_player.state == PlayerStateEnum.playing


async def test_ban_player_by_id(
    players: list[list[PlayerModel]],
    player_dal: PlayerDAL,
):
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    banned_player = await player_dal.ban_player_by_id(player.id)
    assert banned_player.state == PlayerStateEnum.banned
