from polyfactory.factories.pydantic_factory import ModelFactory

from api.schemas.authnetication import UserInTokenSchema


class UserTokenFactory(ModelFactory[UserInTokenSchema]):
    __model__ = UserInTokenSchema
