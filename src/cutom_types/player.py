from typing import Literal

from api.enums import PlayerStateEnum

UPDATE_PLAYER_STATE_TYPE = Literal[
    PlayerStateEnum.waiting,
    PlayerStateEnum.playing,
    PlayerStateEnum.inactive,
]
