from factories.user import UserCreateFactory, UserUpdateFactory
from utilities import choose_from_list

from api.schemas.user import UserCreateSchema, UserUpdateSchema
from database.dals import UserDAL
from database.models.user import UserModel


async def test_get_users(
    default_limit: int,
    users: dict[str, list[UserModel]],
    user_dal: UserDAL,
):
    active_users = await user_dal.get_users(default_limit)
    assert len(active_users) == len(users["active"])
    for user in active_users:
        assert user in users["active"]
    for inactive_user in users["inactive"]:
        assert inactive_user not in active_users


async def test_get_user_by_id(
    users: dict[str, list[UserModel]],
    user_dal: UserDAL,
):
    user = choose_from_list(users["active"])
    fetched_user = await user_dal.get_user_by_id(user.id)
    assert fetched_user == user


async def test_get_user_by_username(
    users: dict[str, list[UserModel]],
    user_dal: UserDAL,
):
    user = choose_from_list(users["active"])
    fetched_user = await user_dal.get_user_by_username(user.username)
    assert fetched_user == user


async def test_create_user(user_dal: UserDAL):
    user_create: UserCreateSchema = UserCreateFactory.build()
    created_user = await user_dal.create_user(user_create)
    assert created_user
    assert created_user.is_active is True

    user_create_dict = user_create.model_dump()
    created_user_dict = created_user.to_dict()
    for field, value in user_create_dict.items():
        assert created_user_dict.pop(field) == value


async def test_update_user_by_id(
    users: dict[str, list[UserModel]],
    user_dal: UserDAL,
):
    user = choose_from_list(users["active"])
    user_update: UserUpdateSchema = UserUpdateFactory.build()
    updated_user = await user_dal.update_user_by_id(
        user_id=user.id,
        user_update=user_update,
    )

    non_updated_user_dict = user.to_dict()
    updated_user_data = user_update.model_dump()
    updated_user_dict = updated_user.to_dict()
    for field, value in updated_user_data.items():
        non_updated_user_dict.pop(field)
        assert updated_user_dict.pop(field) == value
    assert updated_user_dict == non_updated_user_dict


async def test_disable_user(users: dict[str, list[UserModel]], user_dal: UserDAL):
    user = choose_from_list(users["active"])
    disabled_user = await user_dal.disable_user(user.id)
    assert disabled_user.is_active is False
