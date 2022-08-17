# coding: utf-8
import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlmodel import Field, SQLModel, Column, DateTime, func, CheckConstraint

from joby.settings import get_settings


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


class TodoTask(TableBase, table=True):
    __tablename__ = "joby_todo_task"

    todo_at: datetime.datetime | None = Field(sa_column=Column(DateTime(timezone=True), default=None, nullable=True))
    max_retry_on_failure: int | None = Field(default=joby_settings.max_retry_on_failure, nullable=True)
