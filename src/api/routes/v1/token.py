from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from api.interfaces import UserOperationsInterface
from api.schemas.authnetication import TokenSchema

token_router = APIRouter(prefix="/token", tags=["Token"])


@token_router.post("/", response_model=TokenSchema, status_code=status.HTTP_201_CREATED)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    integration_interface: Annotated[UserOperationsInterface, Depends()],
):
    """
    Login user by username and password and return access token.

    :param form_data: username and password form
    :param integration_interface: user operations interface
    :return: tokens
    """
    return await integration_interface.login_user(
        username=form_data.username,
        password=form_data.password,
    )
