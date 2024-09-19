from datetime import datetime, timedelta
from random import randint

DEFAULT_DATE_TIME = datetime(
    year=2024,
    month=9,
    day=1,
    hour=0,
    minute=0,
    second=0,
)

DEFAULT_TIME_DELTA = timedelta(days=1)


def generate_random_timestamp() -> datetime:
    random_int = randint(1, 10_000)
    return DEFAULT_DATE_TIME + timedelta(minutes=random_int)
