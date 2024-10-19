from factories.user import UserCreateFactory, UserUpdateFactory
from utilities import choose_from_list

from api.schemas.user import UserCreateSchema, UserUpdateSchema
from api.services import UserService
from database.models.lobby import LobbyModel
from database.models.player import PlayerModel
from database.models.user import UserModel


async def test_get_users(
    default_limit: int,
    users: dict[str, list[UserModel]],
    user_service: UserService,
):
    active_users = [user.to_dict(exclude={"modified_at"}) for user in users["active"]]
    fetched_users = await user_service.get_users(default_limit)
    assert len(fetched_users) == len(active_users)

    fetched_users_as_dict = [
        user.model_dump(exclude={"modified_at"}) for user in fetched_users
    ]
    for fetched_user in fetched_users_as_dict:
        assert fetched_user in active_users


async def test_get_user_by_id(
    users: dict[str, list[UserModel]],
    lobbies: list[LobbyModel],
    players: list[list[PlayerModel]],
    user_service: UserService,
):
    user = choose_from_list(users["active"])
    fetched_user = await user_service.get_user_by_id(user.id)
    user_as_dict = user.to_dict(exclude={"modified_at"}, include_related=True)
    user_as_dict["players"] = user_as_dict.pop("player_associations")
    assert fetched_user.model_dump(exclude={"modified_at"}) == user_as_dict


async def test_get_user_by_username(
    users: dict[str, list[UserModel]],
    user_service: UserService,
):
    user = choose_from_list(users["active"])
    fetched_user = await user_service.get_user_by_username(user.username)
    fetched_user_as_dict = fetched_user.model_dump(
        exclude={"modified_at", "players", "lobbies"},
    )
    assert fetched_user_as_dict == user.to_dict(exclude={"modified_at"})


async def test_create_user(user_service: UserService):
    user_create: UserCreateSchema = UserCreateFactory.build()
    created_user = await user_service.create_user(user_create)
    for field, value in user_create.model_dump().items():
        assert value == getattr(created_user, field)


async def test_update_user_by_id(
    users: dict[str, list[UserModel]],
    user_service: UserService,
):
    user = choose_from_list(users["active"])
    user_update: UserUpdateSchema = UserUpdateFactory.build()
    updated_user = await user_service.update_user_by_id(user.id, user_update)
    for field, value in user_update.model_dump().items():
        assert value == getattr(updated_user, field)


async def test_disable_user(
    users: dict[str, list[UserModel]],
    user_service: UserService,
):
    user = choose_from_list(users["active"])
    disabled_user = await user_service.disable_user(user.id)
    assert disabled_user.is_active is False
