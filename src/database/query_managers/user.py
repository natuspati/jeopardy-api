from database.models.user import UserModel
from database.query_managers.base import BaseQueryManager


class UserQueryManager(BaseQueryManager):
    _model = UserModel
