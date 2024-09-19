"""Migration queries module."""

from sqlalchemy import Delete, Insert

from database.migrations.data.queries.lobbies import (
    CREATE_LOBBIES_QUERIES,
    DELETE_LOBBIES_QUERIES,
)
from database.migrations.data.queries.players import (
    CREATE_PLAYERS_QUERIES,
    DELETE_PLAYERS_QUERIES,
)
from database.migrations.data.queries.users import (
    CREATE_USERS_QUERIES,
    DELETE_USERS_QUERIES,
)

ORDERED_QUERIES: tuple[tuple[tuple[Insert, ...], tuple[Delete, ...]], ...] = (
    (CREATE_USERS_QUERIES, DELETE_USERS_QUERIES),
    (CREATE_LOBBIES_QUERIES, DELETE_LOBBIES_QUERIES),
    (CREATE_PLAYERS_QUERIES, DELETE_PLAYERS_QUERIES),
)
