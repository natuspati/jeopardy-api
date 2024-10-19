from fixtures.schemas import TestSchema
from polyfactory.factories.pydantic_factory import ModelFactory


class TestSchemaFactory(ModelFactory[TestSchema]):
    __model__ = TestSchema
