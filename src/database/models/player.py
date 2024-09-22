from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.enums import PlayerStateEnum
from database.base_model import BaseDBModelWithID


class PlayerModel(BaseDBModelWithID):
    __tablename__ = "player"

    name: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    state: Mapped[PlayerStateEnum] = mapped_column(
        Enum(PlayerStateEnum),
        default=PlayerStateEnum.waiting,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    lobby_id: Mapped[int] = mapped_column(ForeignKey("lobby.id"), nullable=False)

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="player_associations",
        viewonly=True,
    )
    lobby: Mapped["LobbyModel"] = relationship(
        "LobbyModel",
        back_populates="player_associations",
        viewonly=True,
    )
