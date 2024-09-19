from typing import Annotated

from fastapi import Depends

from api.schemas.nested.user import UserWithLobbiesInDBSchema
from api.schemas.user import UserCreateSchema, UserInDBSchema, UserUpdateSchema
from api.services.mixins import DBModelValidatorMixin
from database.dals import UserDAL


class UserService(DBModelValidatorMixin):
    def __init__(
        self,
        user_dal: Annotated[UserDAL, Depends()],
    ):
        self._user_dal = user_dal

    async def get_users(self, limit: int, offset: int = 0) -> UserInDBSchema:
        """
        Get users.

        :param limit: limit of users to fetch
        :param offset: offset
        :return: users
        """
        users_in_db = await self._user_dal.get_users(
            limit=limit,
            offset=offset,
        )
        return self.validate(users_in_db, UserInDBSchema)

    async def get_user_by_id(self, user_id: int) -> UserWithLobbiesInDBSchema | None:
        """
        Get user by id with associated Lobbies.

        :param user_id: user id
        :return: user with associated Lobbies
        """
        user = await self._user_dal.get_user_by_id(user_id=user_id)
        return self.validate(user, UserWithLobbiesInDBSchema)

    async def get_user_by_username(self, username: str) -> UserInDBSchema | None:
        """
        Get user by username.

        :param username: username
        :return: user
        """
        user = await self._user_dal.get_user_by_username(username)
        return self.validate(user, UserInDBSchema)

    async def create_user(self, user_create: UserCreateSchema) -> UserInDBSchema:
        """
        Create user.

        :param user_create: data to create user
        :return: created user
        """
        created_user = await self._user_dal.create_user(user_create)
        return self.validate(created_user, UserInDBSchema)

    async def update_user_by_id(
        self,
        user_id: int,
        user_update: UserUpdateSchema,
    ) -> UserInDBSchema:
        """
        Update user by id.

        :param user_id: user id
        :param user_update: data to update user
        :return: updated user
        """
        updated_user = await self._user_dal.update_user_by_id(
            user_id=user_id,
            user_update=user_update,
        )
        return self.validate(updated_user, UserInDBSchema)

    async def disable_user(self, user_id: int) -> None:
        """
        Change user status to inactive.

        :param user_id: user id
        :return:
        """
        return await self._user_dal.disable_user(user_id)

    async def total_count(self) -> int:
        """
        Get total number of users.

        :return: total number of users
        """
        return await self._user_dal.total_count()
