from datetime import datetime, timedelta

from sqlalchemy import delete, insert

from api.authnetication import hash_password
from database.migrations.data.commons.timestamps import DEFAULT_DATE_TIME
from database.models.user import UserModel

ACTIVE_USERNAMES = [
    "alice@mail.com",
    "bob@mail.com",
    "coral@mail.com",
    "david@mail.com",
    "eve@mail.com",
    "frank@mail.com",
    "gary@mail.com",
]
INACTIVE_USERNAMES = [
    "hector@mail.com",
    "iris@mail.com",
]
DEFAULT_PASSWORD = "password"


def _create_user(
    username: str,
    creation_time: datetime,
    is_active: bool,
    offset: int,
) -> tuple[dict, int]:
    new_user = {
        "id": offset + 1,
        "username": username,
        "password": hash_password(DEFAULT_PASSWORD),
        "is_active": is_active,
        "created_at": creation_time,
        "modified_at": creation_time,
    }
    return new_user, offset + 1


def _create_users(
    usernames: list[str],
    offset: int,
    is_active: bool = True,
) -> tuple[list[dict], list[int]]:
    new_users = []
    new_user_ids = []
    for i, user_name in enumerate(usernames):
        user_creation_time = DEFAULT_DATE_TIME + timedelta(days=i)
        new_user, offset = _create_user(
            username=user_name,
            creation_time=user_creation_time,
            is_active=is_active,
            offset=offset,
        )
        new_users.append(new_user)
        new_user_ids.append(new_user["id"])
    return new_users, new_user_ids


active_users, active_user_ids = _create_users(
    usernames=ACTIVE_USERNAMES,
    offset=0,
)
inactive_users, inactive_user_ids = _create_users(
    usernames=INACTIVE_USERNAMES,
    offset=active_user_ids[-1],
    is_active=False,
)
all_users = active_users + inactive_users
all_user_ids = active_user_ids + inactive_user_ids


CREATE_USERS_QUERIES = (insert(UserModel).values(all_users),)


DELETE_USERS_QUERIES = (delete(UserModel).where(UserModel.id.in_(all_user_ids)),)
