import asyncio
import os
from logging.config import fileConfig
from typing import Iterable

from alembic import context, util
from alembic.operations import MigrationScript
from alembic.runtime.migration import MigrationContext
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from database.base_model import meta
from database.models import models
from settings import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = meta


def process_revision_directives(  # noqa: WPS210
    context: MigrationContext,
    revision: Iterable[str],
    directives: list[MigrationScript],
) -> None:
    versions_dir = os.path.join(os.path.dirname(__file__), "versions")

    existing_revisions = [
        f
        for f in os.listdir(versions_dir)  # noqa: WPS111
        if f.endswith(".py") and f.split("_")[0].isdigit()
    ]

    if existing_revisions:
        last_revision = sorted(existing_revisions)[-1]
        next_revision_num = int(last_revision.split("_")[0]) + 1
    else:
        next_revision_num = 1

    revision_id = f"{next_revision_num:04d}"

    for directive in directives:
        directive.rev_id = revision_id

    # Inform user
    util.msg(f"Generated revision ID: {revision_id}")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=settings.db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine and associate a connection with the context."""
    connectable = create_async_engine(settings.db_url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
