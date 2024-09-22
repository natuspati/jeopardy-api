from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from database.base_model import IDDBMixin

test_meta = MetaData()


class TestBase(DeclarativeBase):
    metadata = test_meta


class TestDBModel(TestBase, IDDBMixin):
    __tablename__ = "test"

    bool_col: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    date_col: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )
    float_col: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )

    children: Mapped[list["ChildTestDBModel"]] = relationship(
        "ChildTestDBModel",
        back_populates="parent",
    )


class ChildTestDBModel(TestBase, IDDBMixin):
    __tablename__ = "child_test"

    string_col: Mapped[str | None] = mapped_column(String, nullable=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("test.id"), nullable=False)

    parent: Mapped[list["TestDBModel"]] = relationship(
        "TestDBModel",
        back_populates="children",
        viewonly=True,
    )
