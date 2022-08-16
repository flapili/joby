# coding: utf-8
import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Column, DateTime, func, CheckConstraint

from joby.settings import get_settings

# from ..settings import get_settings


joby_settings = get_settings()


class TableBase(SQLModel):
    __table_args__ = (CheckConstraint("created_at <= updated_at"),)

    id: uuid.UUID | None = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    created_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )
    foo: str = Field()


class TodoTask(TableBase, table=True):
    __tablename__ = "joby_todo_task"

    todo_at: datetime.datetime | None = Field(sa_column=Column(DateTime(timezone=True), default=None, nullable=True))
    max_retry_on_failure: int | None = Field(default=joby_settings.max_retry_on_failure, nullable=True)


# sqlite_file_name = "database.db"
# sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine = create_engine(sqlite_url, echo=True)


# def create_db_and_tables():
#     SQLModel.metadata.create_all(engine)


# if __name__ == "__main__":
#     create_db_and_tables()
