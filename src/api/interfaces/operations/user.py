from datetime import timedelta
from typing import Annotated

from fastapi import Depends

from api.authnetication import create_access_token, verify_password
from api.schemas.authnetication import TokenSchema, UserInTokenSchema
from api.schemas.nested.user import UserWithLobbiesInDBSchema
from api.schemas.query import PaginationSchema
from api.schemas.user import (
    PaginatedUsersInDBSchema,
    UserCreateSchema,
    UserInDBSchema,
    UserUpdateSchema,
)
from api.services import LobbyService, UserService
from api.services.pagination import PaginationService
from api.utilities import run_concurrently
from exceptions.service.authorization import InvalidCredentialsError
from exceptions.service.not_found import NotFoundError
from exceptions.service.resource import UserExistsError
from settings import settings


class UserOperationsInterface:
    def __init__(
        self,
        user_service: Annotated[UserService, Depends()],
        lobby_service: Annotated[LobbyService, Depends()],
        pagination_service: Annotated[PaginationService, Depends()],
    ):

        self._users_service = user_service
        self._lobby_service = lobby_service
        self._pagination = pagination_service

    async def get_users(self, pagination: PaginationSchema) -> PaginatedUsersInDBSchema:
        """
        Get users.

        :param pagination: pagination parameters
        :return: paginated list of users
        """
        users, user_count = await run_concurrently(
            self._users_service.get_users(
                limit=pagination.page_size,
                offset=pagination.offset,
            ),
            self._users_service.total_count(),
        )
        self._pagination.configure(pagination)
        return self._pagination.paginate(
            total=user_count,
            items=users,
            result_schema=PaginatedUsersInDBSchema,
        )

    async def get_user(self, user_id: int) -> UserWithLobbiesInDBSchema:
        """
        Get user information with associated Lobbies.

        :param user_id: user id
        :return: user with lobbies
        """
        user = await self._users_service.get_user_by_id(user_id)
        if not user:
            raise NotFoundError()
        return user

    async def login_user(self, username: str, password: str) -> TokenSchema:
        """
        Login user with username and password.

        :param username: username
        :param password: password
        :return: access token
        """
        user = await self._users_service.get_user_by_username(username=username)
        if not user or not verify_password(password, user.password):
            raise InvalidCredentialsError()
        return self._create_access_token(user)

    async def create_user(self, user_create: UserCreateSchema) -> UserInDBSchema:
        """
        Create new user.

        :param user_create: data to create user
        :return: created user
        """
        existing_user = await self._users_service.get_user_by_username(
            username=user_create.username,
        )
        if existing_user:
            raise UserExistsError()
        return await self._users_service.create_user(user_create)

    async def update_user(
        self,
        user_id: int,
        user_update: UserUpdateSchema,
        check: bool = False,
    ) -> UserInDBSchema:
        """
        Update user.

        :param user_id: user
        :param user_update: data to update user
        :param check: check if user exists
        :return: updated user
        """
        if check and await self._users_service.get_user_by_id(user_id):
            raise NotFoundError()
        return await self._users_service.update_user_by_id(
            user_id=user_id,
            user_update=user_update,
        )

    async def disable_user(self, user_id: int, check: bool = False) -> None:
        """
        Change user status to inactive.

        :param user_id: user id
        :param check: check if user exists
        :return:
        """
        if check and await self._users_service.get_user_by_id(user_id):
            raise NotFoundError()
        await self._users_service.disable_user(user_id)

    @classmethod
    def _create_access_token(cls, user: UserInDBSchema) -> TokenSchema:
        access_token_expires = timedelta(minutes=settings.access_token_expire_min)
        token_data = UserInTokenSchema(
            user_id=user.id,
            sub=user.username,
            is_active=user.is_active,
        )
        access_token = create_access_token(
            data=token_data.model_dump(by_alias=True),
            expires_delta=access_token_expires,
        )
        return TokenSchema(access_token=access_token, token_type=settings.token_type)

    @classmethod
    def _verify_password(cls, password: str, user: UserInDBSchema) -> bool:
        return verify_password(plain_password=password, hashed_password=user.password)
