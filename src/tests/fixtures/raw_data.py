from datetime import datetime

import pytest

from api.enums import PlayerStateEnum


@pytest.fixture
def user_raw_data(
    default_timestamp: datetime,
) -> tuple[dict, dict, dict, dict, dict]:
    return (
        {
            "id": 1,
            "username": "adele@mail.com",
            "password": "adele",
            "is_active": True,
            "created_at": default_timestamp,
        },
        {
            "id": 2,
            "username": "beyonce@mail.com",
            "password": "beyonce",
            "is_active": True,
            "created_at": default_timestamp,
        },
        {
            "id": 3,
            "username": "cardib@mail.com",
            "password": "cardib",
            "is_active": True,
            "created_at": default_timestamp,
        },
        {
            "id": 4,
            "username": "drake@mail.com",
            "password": "drake",
            "is_active": False,
            "created_at": default_timestamp,
        },
        {
            "id": 5,
            "username": "eminem@mail.com",
            "password": "eminem",
            "is_active": True,
            "created_at": default_timestamp,
        },
    )


@pytest.fixture
def lobby_raw_data(
    default_timestamp: datetime,
) -> tuple[dict, dict, dict]:
    return (
        {
            "id": 1,
            "name": "First lobby",
            "created_at": default_timestamp,
        },
        {
            "id": 2,
            "name": "Second lobby",
            "created_at": default_timestamp,
        },
        {
            "id": 3,
            "name": "Third lobby",
            "created_at": default_timestamp,
        },
    )


@pytest.fixture
def player_raw_data(
    user_raw_data: tuple[dict, dict, dict, dict, dict],
    lobby_raw_data: tuple[dict, dict, dict],
) -> list[dict[str, int | str | PlayerStateEnum | None]]:
    def get_name_from_user(user: dict) -> str:
        username: str = user["username"].split("@")[0]
        return username.upper()

    def create_player(
        user: dict,
        lobby: dict,
        score: int | None = None,
        state: PlayerStateEnum = PlayerStateEnum.playing,
        offset: int = 0,
    ) -> dict:
        return {
            "id": offset + 1,
            "name": get_name_from_user(adele),
            "score": score,
            "state": state,
            "user_id": user["id"],
            "lobby_id": lobby["id"],
        }

    adele, beyonce, cardib, drake, eminem = user_raw_data
    lobby1, lobby2, lobby3 = lobby_raw_data

    player_configs = [
        # Lobby 1 players
        (adele, lobby1, None, PlayerStateEnum.lead),
        (beyonce, lobby1, 100, PlayerStateEnum.playing),
        (cardib, lobby1, 50, PlayerStateEnum.playing),
        (drake, lobby1, None, PlayerStateEnum.banned),
        # Lobby 2 players
        (eminem, lobby2, None, PlayerStateEnum.lead),
        (cardib, lobby2, None, PlayerStateEnum.waiting),
        (adele, lobby2, None, PlayerStateEnum.waiting),
        # Lobby 3 players
        (beyonce, lobby3, None, PlayerStateEnum.lead),
        (drake, lobby3, None, PlayerStateEnum.banned),
        (eminem, lobby3, 200, PlayerStateEnum.playing),
        (cardib, lobby3, 0, PlayerStateEnum.playing),
    ]

    players = []
    prev_offset = 0
    for player in player_configs:
        players.append(
            create_player(
                user=player[0],
                lobby=player[1],
                score=player[2],
                state=player[3],
                offset=prev_offset,
            ),
        )
        prev_offset += 1
    return players
