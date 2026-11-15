import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = os.path.join(BASE_DIR, ".env")

print(env_path)

load_dotenv(dotenv_path=env_path)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT_POSTGRESQL = os.getenv("DB_PORT_POSTGRESQL", "5432")

DB_PORT = os.getenv("DB_PORT_POSTGRESQL", 5432)


SQLALCHEMY_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Alembic Config object
config = context.config

# Override sqlalchemy.url from env
config.set_main_option("sqlalchemy.url", SQLALCHEMY_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models for autogenerate
from app import models
target_metadata = models.Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=SQLALCHEMY_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
