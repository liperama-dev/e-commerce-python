# Alembic environment configuration.
# This file is executed for every migration command.

import sys
import os

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Make the project root importable so "from app.xxx import yyy" works.
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import application settings and models so autogenerate can detect schema.
from app.config import settings  # noqa: E402
import app.models  # noqa: E402 — registers all ORM models on Base.metadata
from app.database import Base  # noqa: E402

# Alembic Config object (provides access to alembic.ini values).
config = context.config

# Override the sqlalchemy.url from our app config so DATABASE_URL env var wins.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Set up Python logging from the alembic.ini [loggers] section.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode — generate SQL without a live connection.
    Useful for reviewing migration scripts before applying them.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # SQLite requires batch mode for ALTER TABLE operations.
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode — applies changes to a live database.
    This is the mode used by the entrypoint script at container startup.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite requires batch mode for ALTER TABLE / column type changes.
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
