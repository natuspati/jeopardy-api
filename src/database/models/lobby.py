from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_model import BaseDBModelWithID


class LobbyModel(BaseDBModelWithID):
    __tablename__ = "lobby"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    player_associations: Mapped[list["PlayerModel"]] = relationship(
        "PlayerModel",
        back_populates="lobby",
    )
    users: Mapped[list["UserModel"]] = relationship(
        "UserModel",
        secondary="player",
        back_populates="lobbies",
        viewonly=True,
    )
