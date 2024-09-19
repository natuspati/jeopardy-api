import asyncio
import logging
from typing import Literal

import click

from database.migrations.data.run import run_data_migrations
from exceptions.module.cli import InvalidCLIArgumentsError
from exceptions.module.database import DatabaseDetailError

logger = logging.getLogger(__name__)


@click.command()
@click.argument("direction", type=click.Choice(["up", "down"], case_sensitive=False))
def migrate_data(direction: Literal["up", "down"]) -> None:
    """
    CLI command to run data migrations.

    Usage:
        python run.py up
        python run.py down
    """
    match direction:
        case "up":
            direction = True
        case "down":
            direction = False
        case _:
            raise InvalidCLIArgumentsError(direction)

    try:
        asyncio.run(run_data_migrations(direction))
    except DatabaseDetailError as error:
        logger.error(f"Could not make migrations, error details: {error.detail}")


if __name__ == "__main__":
    migrate_data()
