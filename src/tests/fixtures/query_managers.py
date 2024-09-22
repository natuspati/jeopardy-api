from database.query_managers.base import BaseQueryManager
from tests.fixtures.models import ChildTestDBModel, TestDBModel


class TestQueryManager(BaseQueryManager):
    _model = TestDBModel
    _association_models = {
        "children": {
            "model": ChildTestDBModel,
            "on": TestDBModel.id == ChildTestDBModel.parent_id,
            "isouter": False,
        },
    }
