import pytest
from factories.user import UserCreateFactory, UserUpdateFactory
from sqlalchemy.ext.asyncio import AsyncSession
from utilities import choose_from_list

from api.authnetication import decode_token
from api.interfaces import UserOperationsInterface
from api.schemas.query import PaginationSchema
from api.schemas.user import UserCreateSchema, UserUpdateSchema
from database.models.player import PlayerModel
from database.models.user import UserModel
from exceptions.service.authorization import InvalidCredentialsError


@pytest.mark.usefixtures("_reset_database")
async def test_get_users(
    users: dict[str, list[UserModel]],
    pagination_schema: PaginationSchema,
    db_session: AsyncSession,
    user_operations: UserOperationsInterface,
):
    await db_session.commit()
    paginated_users = await user_operations.get_users(pagination_schema)
    assert len(paginated_users.items) == len(users)
    assert paginated_users.page == pagination_schema.page

    total_user_count = len(users["active"]) + len(users["inactive"])
    assert paginated_users.total == total_user_count

    assert str(pagination_schema.page + 1) in paginated_users.next
    assert str(pagination_schema.page_size) in paginated_users.next
    assert paginated_users.previous is None


async def test_get_user(
    users: dict[str, list[UserModel]],
    players: list[list[PlayerModel]],
    user_operations: UserOperationsInterface,
):
    user = choose_from_list(users["active"])
    fetched_user = await user_operations.get_user(user.id)

    user_as_dict = user.to_dict(exclude={"modified_at"}, include_related=True)
    user_as_dict["players"] = user_as_dict.pop("player_associations")
    fetched_user_as_dict = fetched_user.model_dump(
        exclude={"modified_at"},
    )
    assert fetched_user_as_dict == user_as_dict


async def test_login_user(
    users: dict[str, list[UserModel]],
    user_operations: UserOperationsInterface,
):
    user = choose_from_list(users["active"])
    user_password = user.username.split("@")[0]
    token = await user_operations.login_user(
        username=user.username,
        password=user_password,
    )
    assert token.access_token

    payload = decode_token(token.access_token)
    assert payload.user_id == user.id
    assert payload.username == user.username


async def test_create_user(
    user_operations: UserOperationsInterface,
):
    user_create: UserCreateSchema = UserCreateFactory.build()
    created_user = await user_operations.create_user(user_create)
    for field, value in user_create.model_dump().items():
        assert value == getattr(created_user, field)


async def test_update_user(
    users: dict[str, list[UserModel]],
    user_operations: UserOperationsInterface,
):
    user = choose_from_list(users["active"])
    user_update: UserUpdateSchema = UserUpdateFactory.build()
    updated_user = await user_operations.update_user(user.id, user_update)
    for field, value in user_update.model_dump().items():
        assert value == getattr(updated_user, field)


async def test_disable_user(
    users: dict[str, list[UserModel]],
    user_operations: UserOperationsInterface,
):
    user = choose_from_list(users["active"])
    user_password = user.username.split("@")[0]
    await user_operations.disable_user(user.id)
    with pytest.raises(InvalidCredentialsError):
        await user_operations.login_user(
            username=user.username,
            password=user_password,
        )
