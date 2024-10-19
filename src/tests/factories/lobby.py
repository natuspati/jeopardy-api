from polyfactory.factories.pydantic_factory import ModelFactory

from api.schemas.lobby import LobbyPlayerCreateSchema
from api.schemas.player import LobbyPlayerAddSchema


class LobbyPlayerCreateFactory(ModelFactory[LobbyPlayerCreateSchema]):
    __model__ = LobbyPlayerCreateSchema


class LobbyPlayerAddFactory(ModelFactory[LobbyPlayerAddSchema]):
    __model__ = LobbyPlayerAddSchema
