from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from api.schemas.user import UserCreateSchema, UserInDBSchema, UserUpdateSchema
from database.models.user import UserModel


class UserFactory(SQLAlchemyFactory[UserModel]):
    __model__ = UserModel


class UserCreateFactory(ModelFactory[UserCreateSchema]):
    __model__ = UserCreateSchema


class UserUpdateFactory(ModelFactory[UserUpdateSchema]):
    __model__ = UserUpdateSchema


class UserInDBFactory(ModelFactory[UserInDBSchema]):
    __model__ = UserInDBSchema
