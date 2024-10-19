import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from api.dependencies import get_current_user, get_pagination_parameters
from api.dependencies.authorization import check_current_user
from api.interfaces import UserOperationsInterface
from api.schemas.nested.user import UserWithLobbiesShowSchema
from api.schemas.query import PaginationSchema
from api.schemas.user import (
    PaginatedUsersShowSchema,
    UserCreateSchema,
    UserShowSchema,
    UserUpdateSchema,
)
from exceptions.responses import (
    FORBIDDEN_RESPONSE,
    REQUEST_ERROR_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    generate_responses,
)

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get(
    "/",
    response_model=PaginatedUsersShowSchema,
    responses=generate_responses(UNAUTHORIZED_RESPONSE, REQUEST_ERROR_RESPONSE),
    dependencies=[Depends(get_current_user)],
)
async def get_users(
    pagination: Annotated[PaginationSchema, Depends(get_pagination_parameters)],
    integration_interface: Annotated[UserOperationsInterface, Depends()],
):
    """
    Get list of users.

    :param pagination: pagination query parameters
    :param integration_interface: user operations interface
    :return: paginated list of users
    """
    return await integration_interface.get_users(pagination=pagination)


@user_router.get(
    "/{user_id}/",
    response_model=UserWithLobbiesShowSchema,
    responses=generate_responses(
        UNAUTHORIZED_RESPONSE,
        FORBIDDEN_RESPONSE,
        (status.HTTP_404_NOT_FOUND, "User not found"),
    ),
    dependencies=[Depends(check_current_user)],
)
async def get_user_by_id(
    user_id: int,
    integration_interface: Annotated[UserOperationsInterface, Depends()],
):
    """
    Get user details with associated lobbies.

    :param user_id: user id
    :param integration_interface: user operations interface
    :return: user with associated lobbies
    """
    return await integration_interface.get_user(user_id)


@user_router.post(
    "/",
    response_model=UserShowSchema,
    status_code=status.HTTP_201_CREATED,
    responses=generate_responses(
        (status.HTTP_422_UNPROCESSABLE_ENTITY, "User data invalid"),
        (status.HTTP_409_CONFLICT, "User already registered"),
    ),
)
async def create_user(
    user_create: UserCreateSchema,
    integration_interface: Annotated[UserOperationsInterface, Depends()],
):
    """
    Create a new user.

    :param user_create: data to create user
    :param integration_interface: user operations interface
    :return: created user
    """
    return await integration_interface.create_user(user_create)


@user_router.patch(
    "/{user_id}/",
    response_model=UserShowSchema,
    responses=generate_responses(
        UNAUTHORIZED_RESPONSE,
        FORBIDDEN_RESPONSE,
        (status.HTTP_404_NOT_FOUND, "User not found"),
        (status.HTTP_422_UNPROCESSABLE_ENTITY, "User data invalid"),
    ),
    dependencies=[Depends(check_current_user)],
)
async def update_user(
    user_id: int,
    user_update: UserUpdateSchema,
    integration_interface: Annotated[UserOperationsInterface, Depends()],
):
    """
    Update user details.

    :param user_id: user id
    :param user_update: data to update user
    :param integration_interface: user operations interface
    :return: updated user
    """
    return await integration_interface.update_user(
        user_id=user_id,
        user_update=user_update,
    )


@user_router.delete(
    "/{user_id}/",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=generate_responses(
        UNAUTHORIZED_RESPONSE,
        FORBIDDEN_RESPONSE,
        (status.HTTP_404_NOT_FOUND, "User not found"),
    ),
    dependencies=[Depends(check_current_user)],
)
async def delete_user(
    user_id: int,
    integration_interface: Annotated[UserOperationsInterface, Depends()],
):
    """
    Disable user.

    :param user_id: user id
    :param integration_interface: user operations interface
    :return:
    """
    await integration_interface.disable_user(user_id)
