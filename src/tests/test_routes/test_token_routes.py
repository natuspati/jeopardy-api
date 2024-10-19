import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from api.authnetication import decode_token
from database.models.user import UserModel


@pytest.mark.usefixtures("_reset_database")
async def test_login_for_access_token(
    active_user: UserModel,
    password: str,
    db_session: AsyncSession,
    http_client: TestClient,
):
    await db_session.commit()
    url = http_client.app.url_path_for("login_for_access_token")
    response = http_client.post(
        url,
        data={"username": active_user.username, "password": password},
    )
    assert response.status_code == status.HTTP_201_CREATED

    access_token = response.json().get("access_token")
    assert access_token
    payload = decode_token(access_token)
    assert payload.user_id == active_user.id
    assert payload.username == active_user.username
