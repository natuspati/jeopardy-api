from polyfactory.factories.pydantic_factory import ModelFactory

from api.schemas.authnetication import TokenDataSchema


class TokenDataFactory(ModelFactory[TokenDataSchema]):
    __model__ = TokenDataSchema
