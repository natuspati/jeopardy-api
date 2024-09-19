from enum import Enum


class PlayerStateEnum(Enum):
    lead = "lead"
    waiting = "waiting"
    playing = "playing"
    inactive = "inactive"
    banned = "banned"
