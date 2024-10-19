from datetime import datetime

import pytest
from sqlalchemy import URL

from settings import settings


@pytest.fixture(scope="session")
def test_db_url() -> URL:
    return settings.db_url.set(database="test")


@pytest.fixture(scope="session")
def default_id() -> int:
    return 1


@pytest.fixture(scope="session")
def default_timestamp() -> datetime:
    return datetime(year=2024, month=1, day=1)


@pytest.fixture(scope="session")
def default_limit() -> int:
    return 10


@pytest.fixture(scope="session")
def default_page() -> int:
    return 1


@pytest.fixture(scope="session")
def default_page_size() -> int:
    return 2


@pytest.fixture(scope="session")
def batch_size() -> int:
    return 10
