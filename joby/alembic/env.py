from sqlalchemy.engine import Connection
import sqlmodel

from alembic import context

import joby.models.db  # noqa: F401

config = context.config
target_metadata = sqlmodel.SQLModel.metadata


def run_migrations_online() -> None:
    conn: Connection = config.attributes["connection"]
    context.configure(connection=conn, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
