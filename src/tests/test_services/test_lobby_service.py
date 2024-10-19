from utilities import choose_from_list

from api.services import LobbyService
from database.models.lobby import LobbyModel
from database.models.player import PlayerModel


async def test_get_lobbies(
    default_limit: int,
    lobbies: list[LobbyModel],
    lobby_service: LobbyService,
):
    fetched_lobbies = await lobby_service.get_lobbies(default_limit)
    assert len(fetched_lobbies) == len(lobbies)
    lobbies_as_dicts = [lobby.to_dict() for lobby in lobbies]
    for fetched_lobby in fetched_lobbies:
        assert fetched_lobby.model_dump() in lobbies_as_dicts


async def test_get_lobby_by_id(
    lobbies: list[LobbyModel],
    players: list[list[PlayerModel]],
    lobby_service: LobbyService,
):
    players_in_lobby = choose_from_list(players)
    player_in_lobby = choose_from_list(players_in_lobby)
    selected_lobby = lobbies[player_in_lobby.lobby_id - 1]
    fetched_lobby = await lobby_service.get_lobby_by_id(selected_lobby.id)

    assert fetched_lobby.model_dump(exclude={"players"}) == selected_lobby.to_dict()
    assert len(fetched_lobby.players) == len(players_in_lobby)
    players_as_dict = [player.to_dict() for player in players_in_lobby]
    for player in fetched_lobby.players:
        assert player.model_dump() in players_as_dict
