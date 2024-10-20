import pytest
from factories.lobby import LobbyPlayerAddFactory, LobbyPlayerCreateFactory
from sqlalchemy.ext.asyncio import AsyncSession
from utilities import choose_from_list

from api.enums import PlayerStateEnum
from api.interfaces import LobbyOperationsInterface
from api.schemas.query import DateTimeSchema, OrderSchema, PaginationSchema
from database.models.lobby import LobbyModel
from database.models.player import PlayerModel
from database.models.user import UserModel
from exceptions.service.authorization import (
    BannedPlayerStatusError,
    InsufficientPlayerStatusError,
)
from exceptions.service.lobby import PlayerLobbyDoesNotMatchError
from exceptions.service.resource import PlayerExistsError


@pytest.mark.usefixtures("_reset_database")
async def test_get_lobbies(
    lobbies: list[LobbyModel],
    pagination_schema: PaginationSchema,
    date_schema: DateTimeSchema,
    order_schema: OrderSchema,
    db_session: AsyncSession,
    lobby_operations: LobbyOperationsInterface,
):
    await db_session.commit()
    paginated_lobbies = await lobby_operations.get_lobbies(
        pagination=pagination_schema,
        date=date_schema,
        order=order_schema,
    )
    fetched_lobbies = paginated_lobbies.items
    assert len(fetched_lobbies) == pagination_schema.page_size
    assert paginated_lobbies.total == len(lobbies)
    for ind in range(len(fetched_lobbies) - 1):
        prev_lobby = fetched_lobbies[ind]
        next_lobby = fetched_lobbies[ind + 1]
        assert prev_lobby.created_at >= next_lobby.created_at


async def test_get_lobby(
    lobbies: list[LobbyModel],
    players: list[list[PlayerModel]],
    lobby_operations: LobbyOperationsInterface,
):
    players_in_lobby = choose_from_list(players)
    player_in_lobby = choose_from_list(players_in_lobby)
    selected_lobby = lobbies[player_in_lobby.lobby_id - 1]
    fetched_lobby = await lobby_operations.get_lobby(selected_lobby.id)

    assert fetched_lobby.model_dump(exclude={"players"}) == selected_lobby.to_dict()
    assert len(fetched_lobby.players) == len(players_in_lobby)
    players_as_dict = [player.to_dict() for player in players_in_lobby]
    for player in fetched_lobby.players:
        assert player.model_dump() in players_as_dict


async def test_get_player(
    players: list[list[PlayerModel]],
    lobby_operations: LobbyOperationsInterface,
):
    players_in_lobby = choose_from_list(players)
    player_in_lobby = choose_from_list(players_in_lobby)
    fetched_player = await lobby_operations.get_player(
        lobby_id=player_in_lobby.lobby_id,
        player_id=player_in_lobby.id,
    )
    assert fetched_player.model_dump() == player_in_lobby.to_dict(include_related=True)


async def test_get_player_with_wrong_lobby_fails(
    players: list[list[PlayerModel]],
    lobby_operations: LobbyOperationsInterface,
):
    players_in_lobby = choose_from_list(players)
    player_in_lobby = choose_from_list(players_in_lobby)
    with pytest.raises(PlayerLobbyDoesNotMatchError):
        await lobby_operations.get_player(
            lobby_id=player_in_lobby.lobby_id + 1,
            player_id=player_in_lobby.id,
        )


async def test_ban_player(
    players: list[list[PlayerModel]],
    lobby_operations: LobbyOperationsInterface,
):
    players_in_lobby = choose_from_list(players)
    lead_player = None
    for ind, player in enumerate(players_in_lobby):
        if player.state == PlayerStateEnum.lead:
            lead_player = player
            players_in_lobby.pop(ind)
    if not lead_player:
        pytest.fail("No lead player in selected lobby.")
    player_in_lobby = choose_from_list(players_in_lobby)

    with pytest.raises(PlayerLobbyDoesNotMatchError):
        await lobby_operations.ban_player(
            lobby_id=player_in_lobby.lobby_id + 1,
            lead_player_id=lead_player.id,
            player_id=player_in_lobby.id,
        )

    with pytest.raises(InsufficientPlayerStatusError):
        await lobby_operations.ban_player(
            lobby_id=player_in_lobby.lobby_id,
            lead_player_id=player_in_lobby.id,
            player_id=player_in_lobby.id,
        )

    banned_player = await lobby_operations.ban_player(
        lobby_id=player_in_lobby.lobby_id,
        lead_player_id=lead_player.id,
        player_id=player_in_lobby.id,
    )
    assert banned_player.state == PlayerStateEnum.banned


async def test_create_lobby(
    active_user: UserModel,
    lobby_operations: LobbyOperationsInterface,
):
    lobby_create = LobbyPlayerCreateFactory.build()
    lobby = await lobby_operations.create_lobby(
        user_id=active_user.id,
        lobby_player_create=lobby_create,
    )
    assert lobby.name == lobby_create.lobby_name
    assert len(lobby.players) == 1
    created_player = lobby.players[0]
    assert created_player.name == lobby_create.player_name
    assert created_player.user_id == active_user.id
    assert created_player.state == PlayerStateEnum.lead


async def test_create_waiting_player(
    active_user: UserModel,
    lobbies: list[LobbyModel],
    lobby_operations: LobbyOperationsInterface,
):
    lobby = choose_from_list(lobbies)
    player_add = LobbyPlayerAddFactory.build()
    created_player = await lobby_operations.create_waiting_player(
        lobby_id=lobby.id,
        user_id=active_user.id,
        lobby_player_add=player_add,
    )
    assert created_player.name == player_add.name
    assert created_player.state == PlayerStateEnum.waiting
    assert created_player.lobby_id == lobby.id
    assert created_player.user_id == active_user.id


async def test_create_waiting_player_fails_if_banned_or_existing(
    players: list[list[PlayerModel]],
    lobby_operations: LobbyOperationsInterface,
):
    existing_player, banned_player = None, None
    for player in players[0]:
        if player.state == PlayerStateEnum.banned:
            banned_player = player
        else:
            existing_player = player
    if not existing_player or not banned_player:
        pytest.fail("First lobby must have non banned and banned player")
    player_add = LobbyPlayerAddFactory.build()

    with pytest.raises(BannedPlayerStatusError):
        await lobby_operations.create_waiting_player(
            lobby_id=banned_player.lobby_id,
            user_id=banned_player.user_id,
            lobby_player_add=player_add,
        )
    with pytest.raises(PlayerExistsError):
        await lobby_operations.create_waiting_player(
            lobby_id=existing_player.lobby_id,
            user_id=existing_player.user_id,
            lobby_player_add=player_add,
        )


async def test_start_lobby(
    players: list[list[PlayerModel]],
    lobby_operations: LobbyOperationsInterface,
):
    lobby_id = 3
    players_in_waiting_lobby = players[lobby_id - 1]
    waiting_players = [
        player
        for player in players_in_waiting_lobby
        if player.state == PlayerStateEnum.waiting
    ]
    if not waiting_players:
        pytest.fail("Third lobby must have waiting players")
    started_lobby = await lobby_operations.start_lobby(lobby_id)
    for player in started_lobby.players:
        assert player.state not in {PlayerStateEnum.waiting, PlayerStateEnum.inactive}
    assert started_lobby.get_lead()
