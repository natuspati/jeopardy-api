from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base_model import BaseDBModelWithID


class UserModel(BaseDBModelWithID):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    player_associations: Mapped[list["PlayerModel"]] = relationship(
        "PlayerModel",
        back_populates="user",
    )
    lobbies: Mapped[list["LobbyModel"]] = relationship(
        "LobbyModel",
        secondary="player",
        back_populates="users",
        viewonly=True,
    )
