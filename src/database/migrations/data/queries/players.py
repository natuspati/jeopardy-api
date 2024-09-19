from random import randint

from sqlalchemy import delete, insert

from api.enums import PlayerStateEnum
from database.migrations.data.queries.lobbies import lobby_ids
from database.migrations.data.queries.users import active_users as users
from database.models.player import PlayerModel


def _create_players() -> tuple[list[dict], list[int]]:
    players = []
    start_id_offset = 0
    inactive_lobby_players, id_offset = _create_players_in_inactive_lobby(
        start_id_offset,
    )
    players.extend(inactive_lobby_players)

    inactive_lobby_players, id_offset = _create_players_in_active_lobby(id_offset)
    players.extend(inactive_lobby_players)

    new_lobby_players, id_offset = _create_players_in_new_lobby(id_offset)
    players.extend(new_lobby_players)

    player_ids = list(range(start_id_offset, id_offset + 1))
    return players, player_ids


def _create_players_in_inactive_lobby(id_offset: int) -> tuple[list[dict], int]:
    lobby_id = lobby_ids[0]
    lead_user = users[6]
    regular_users = [users[1], users[5], users[2], users[4]]
    banned_users = [users[0]]
    lobby_players = []

    lead_player = _create_lead_player(
        lobby_id=lobby_id,
        lead_user=lead_user,
        id_offset=id_offset,
    )
    lobby_players.append(lead_player)

    regular_players = _create_regular_players(
        lobby_id=lobby_id,
        regular_users=regular_users,
        id_offset=lead_player["id"],
    )
    lobby_players.extend(regular_players)

    banned_players = _create_banned_players(
        lobby_id=lobby_id,
        banned_users=banned_users,
        id_offset=regular_players[-1]["id"],
    )
    lobby_players.extend(banned_players)
    return lobby_players, lobby_players[-1]["id"]


def _create_players_in_active_lobby(id_offset: int) -> tuple[list[dict], int]:
    lobby_id = lobby_ids[1]
    lead_user = users[3]
    regular_users = [users[4], users[0], users[6], users[2]]
    banned_users = [users[5], users[1]]
    lobby_players = []

    lead_player = _create_lead_player(
        lobby_id=lobby_id,
        lead_user=lead_user,
        id_offset=id_offset,
    )
    lobby_players.append(lead_player)

    regular_players = _create_regular_players(
        lobby_id=lobby_id,
        regular_users=regular_users,
        id_offset=lead_player["id"],
        state=PlayerStateEnum.playing,
    )
    lobby_players.extend(regular_players)

    banned_players = _create_banned_players(
        lobby_id=lobby_id,
        banned_users=banned_users,
        id_offset=regular_players[-1]["id"],
    )
    lobby_players.extend(banned_players)
    return lobby_players, lobby_players[-1]["id"]


def _create_players_in_new_lobby(id_offset: int) -> tuple[list[dict], int]:
    lobby_id = lobby_ids[2]
    lead_user = users[3]
    regular_users = [users[4], users[1], users[5]]
    lobby_players = []

    lead_player = _create_lead_player(
        lobby_id=lobby_id,
        lead_user=lead_user,
        id_offset=id_offset,
    )
    lobby_players.append(lead_player)

    regular_players = _create_regular_players(
        lobby_id=lobby_id,
        regular_users=regular_users,
        id_offset=lead_player["id"],
        put_score=False,
    )
    lobby_players.extend(regular_players)
    return lobby_players, lobby_players[-1]["id"]


def _create_lead_player(
    lobby_id: int,
    lead_user: dict,
    id_offset: int,
) -> dict:
    return {
        "id": id_offset + 1,
        "name": _player_name_from_username(lead_user),
        "score": None,
        "state": PlayerStateEnum.lead,
        "user_id": lead_user["id"],
        "lobby_id": lobby_id,
    }


def _create_regular_players(
    lobby_id: int,
    regular_users: list[dict],
    id_offset: int,
    put_score: bool = True,
    state: PlayerStateEnum = PlayerStateEnum.waiting,
) -> list[dict]:
    regular_players = []
    for i, user in enumerate(regular_users):
        player = {
            "id": id_offset + i + 1,
            "name": _player_name_from_username(user),
            "score": _random_score() if put_score else None,
            "state": state,
            "user_id": user["id"],
            "lobby_id": lobby_id,
        }
        regular_players.append(player)
    return regular_players


def _create_banned_players(
    lobby_id: int,
    banned_users: list[dict],
    id_offset: int,
    put_score: bool = True,
) -> list[dict]:
    banned_players = []
    for i, user in enumerate(banned_users):
        player = {
            "id": id_offset + i + 1,
            "name": _player_name_from_username(user),
            "score": _random_score() if put_score else None,
            "state": PlayerStateEnum.banned,
            "user_id": user["id"],
            "lobby_id": lobby_id,
        }
        banned_players.append(player)
    return banned_players


def _player_name_from_username(user: dict[str, str]) -> str:
    username = user["username"].split("@")[0]
    return username.title()


def _random_score() -> int:
    return randint(-10_000, 10_000)


PLAYERS, PLAYER_IDS = _create_players()

CREATE_PLAYERS_QUERIES = (insert(PlayerModel).values(PLAYERS),)
DELETE_PLAYERS_QUERIES = (delete(PlayerModel).where(PlayerModel.id.in_(PLAYER_IDS)),)
