import pytest
from utilities import choose_from_list

from api.enums import PlayerStateEnum
from api.services import PlayerService
from database.models.player import PlayerModel
from exceptions.service.player import UpdatePlayerStateInvalidError


async def test_get_player_by_id(
    players: list[list[PlayerModel]],
    player_service: PlayerService,
):
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    fetched_player = await player_service.get_player_by_id(player.id)
    assert fetched_player.model_dump() == player.to_dict(include_related=True)


async def test_update_state_by_lobby_id(
    players: list[list[PlayerModel]],
    player_service: PlayerService,
):
    lobby_id = 3
    players_in_waiting_lobby = players[lobby_id - 1]
    waiting_players, other_players = [], []
    for player in players_in_waiting_lobby:
        if player.state == PlayerStateEnum.waiting:
            waiting_players.append(player)
        else:
            other_players.append(player)
    if not waiting_players:
        pytest.fail("Third lobby must have waiting players")
    inactive_players = await player_service.update_state_by_lobby_id(
        lobby_id=lobby_id,
        state=PlayerStateEnum.inactive,
    )
    assert len(waiting_players) == len(inactive_players)
    for inactive_player in inactive_players:
        assert inactive_player.state == PlayerStateEnum.inactive
    for other_player in other_players:
        not_updated_player = await player_service.get_player_by_id(other_player.id)
        assert not_updated_player.state == other_player.state


@pytest.mark.parametrize(
    "state",
    [PlayerStateEnum.lead, PlayerStateEnum.banned],
)
async def test_update_state_by_lobby_id_fails_if_invalid_state(
    state: PlayerStateEnum,
    player_service: PlayerService,
):
    with pytest.raises(UpdatePlayerStateInvalidError):
        await player_service.update_state_by_lobby_id(
            lobby_id=1,
            state=state,
        )


async def test_ban_player_by_id(
    players: list[list[PlayerModel]],
    player_service: PlayerService,
):
    players_in_lobby = choose_from_list(players)
    player = choose_from_list(players_in_lobby)
    banned_player = await player_service.ban_player_by_id(player.id)
    assert banned_player.state == PlayerStateEnum.banned
