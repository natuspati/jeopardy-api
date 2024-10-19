import pytest
from factories.user import UserCreateFactory, UserUpdateFactory
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utilities import choose_from_list, create_auth_header

from api.schemas.query import PaginationSchema
from api.schemas.user import UserCreateSchema, UserShowSchema, UserUpdateSchema
from database.manager import DatabaseConnectionManager
from database.models.player import PlayerModel
from database.models.user import UserModel


@pytest.mark.usefixtures("_reset_database")
async def test_get_users(
    users: dict[str, list[UserModel]],
    db_session: AsyncSession,
    pagination_schema: PaginationSchema,
    auth_client: TestClient,
):
    await db_session.commit()
    url = auth_client.app.url_path_for("get_users")
    response = auth_client.get(url=url, params=pagination_schema.model_dump())
    assert response.status_code == status.HTTP_200_OK

    content: dict = response.json()
    active_users = [
        UserShowSchema.model_validate(user.to_dict()) for user in users["active"]
    ]
    fetched_users = [UserShowSchema.model_validate(user) for user in content["items"]]
    for fetched_user in fetched_users:
        assert fetched_user in active_users


@pytest.mark.usefixtures("_reset_database")
async def test_get_user_by_id(
    users: dict[str, list[UserModel]],
    players: list[list[PlayerModel]],
    db_session: AsyncSession,
    http_client: TestClient,
):
    await db_session.commit()
    user = choose_from_list(users["active"])
    url = http_client.app.url_path_for("get_user_by_id", user_id=user.id)
    response = http_client.get(url=url, headers=create_auth_header(user))
    assert response.status_code == status.HTTP_200_OK
    fetched_user = response.json()

    user_player_count = 0
    user_lobby_count = 0
    for players_in_lobby in players:
        if any(player.user_id == user.id for player in players_in_lobby):
            user_player_count += 1
            user_lobby_count += 1
    assert len(fetched_user.pop("players")) == user_player_count
    assert len(fetched_user.pop("lobbies")) == user_lobby_count

    fetched_user.pop("created_at")
    fetched_user.pop("modified_at")
    user_dict = user.to_dict(
        exclude={"password", "is_active", "created_at", "modified_at"},
    )
    assert fetched_user == user_dict


@pytest.mark.usefixtures("_setup_database", "_reset_database")
async def test_create_user(http_client: TestClient):
    user_create: UserCreateSchema = UserCreateFactory.build()
    url = http_client.app.url_path_for("create_user")
    response = http_client.post(url=url, json=user_create.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
    created_user = response.json()
    assert created_user["username"] == user_create.username


@pytest.mark.usefixtures("_reset_database")
async def test_update_user(
    users: dict[str, list[UserModel]],
    db_session: AsyncSession,
    http_client: TestClient,
):
    await db_session.commit()
    user = choose_from_list(users["active"])
    user_update: UserUpdateSchema = UserUpdateFactory.build()
    user_update_dict = user_update.model_dump()
    url = http_client.app.url_path_for("update_user", user_id=user.id)
    response = http_client.patch(
        url=url,
        json=user_update_dict,
        headers=create_auth_header(user),
    )
    assert response.status_code == status.HTTP_200_OK

    updated_user = response.json()
    for updated_field, updated_value in user_update_dict.items():
        assert updated_user.pop(updated_field) == updated_value


@pytest.mark.usefixtures("_reset_database")
async def test_delete_user(
    users: dict[str, list[UserModel]],
    db_session: AsyncSession,
    db_manager: DatabaseConnectionManager,
    http_client: TestClient,
):
    await db_session.commit()
    user = choose_from_list(users["active"])
    url = http_client.app.url_path_for("delete_user", user_id=user.id)
    response = http_client.delete(url=url, headers=create_auth_header(user))
    assert response.status_code == status.HTTP_204_NO_CONTENT

    async with db_manager.session() as session:
        # noinspection PyTypeChecker
        select_user_query = select(UserModel).where(UserModel.id == user.id)
        deleted_user: UserModel = await session.scalar(select_user_query)
        assert not deleted_user.is_active
