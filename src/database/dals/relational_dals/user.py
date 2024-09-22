from api.schemas.user import UserCreateSchema, UserUpdateSchema
from database.dals.relational_dals.base import BaseDAL
from database.models.user import UserModel
from database.query_managers import UserQueryManager


class UserDAL(BaseDAL):
    _qm = UserQueryManager

    async def get_users(self, limit: int, offset: int | None = 0) -> list[UserModel]:
        """
        Get active users.

        :param limit:  limit of users to fetch
        :param offset: offset
        :return: list of users
        """
        return await self.select(
            many=True,
            limit=limit,
            offset=offset,
            where={"is_active": True},
        )

    async def get_user_by_id(self, user_id: int) -> UserModel | None:
        """
        Get user by id with their lobbies and players.

        If user is not active, return None.

        :param user_id: user id
        :return: user with lobbies and players.
        """
        return await self.select(
            where={"id": user_id, "is_active": True},
            related=["lobbies", "player_associations"],
        )

    async def get_user_by_username(self, username: str) -> UserModel | None:
        """
        Get user by username.

        If user is not active, return None.

        :param username: username
        :return: user
        """
        return await self.select(where={"username": username, "is_active": True})

    async def create_user(self, user_create: UserCreateSchema) -> UserModel:
        """
        Create new user.

        :param user_create: user create data
        :return: created user
        """
        return await self.insert(**user_create.model_dump())

    async def update_user_by_id(
        self,
        user_id: int,
        user_update: UserUpdateSchema,
    ) -> UserModel:
        """
        Update user by id.

        :param user_id: user id
        :param user_update: user update data
        :return: updated user
        """
        return await self.update(where={"id": user_id}, **user_update.model_dump())

    async def disable_user(self, user_id: int) -> UserModel:
        """
        Disable user by id.

        :param user_id: user id
        :return: disabled user
        """
        return await self.update(where={"id": user_id}, is_active=False)
