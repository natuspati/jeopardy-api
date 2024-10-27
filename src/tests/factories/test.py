from fixtures.schemas import MockSchema
from polyfactory.factories.pydantic_factory import ModelFactory


class TestSchemaFactory(ModelFactory[MockSchema]):
    __model__ = MockSchema
