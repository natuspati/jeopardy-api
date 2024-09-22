from utilities import choose_from_list

from database.dals import LobbyDAL
from database.models.lobby import LobbyModel
from database.models.player import PlayerModel


async def test_get_lobbies(
    default_limit: int,
    lobbies: list[LobbyModel],
    lobby_dal: LobbyDAL,
):
    fetched_lobbies = await lobby_dal.get_lobbies(default_limit)
    assert len(fetched_lobbies) == len(lobbies)
    for lobby in fetched_lobbies:
        assert lobby in lobbies


async def test_get_lobby_by_id(
    lobbies: list[LobbyModel],
    players: list[list[PlayerModel]],
    lobby_dal: LobbyDAL,
):
    players_in_lobby = choose_from_list(players)
    player_in_lobby: PlayerModel = choose_from_list(players_in_lobby)
    selected_lobby = lobbies[player_in_lobby.lobby_id - 1]

    fetched_lobby = await lobby_dal.get_lobby_by_id(selected_lobby.id)
    assert fetched_lobby == selected_lobby
    assert len(fetched_lobby.player_associations) == len(players_in_lobby)
    for player in fetched_lobby.player_associations:
        assert player in players_in_lobby
