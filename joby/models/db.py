# coding: utf-8
import datetime
from typing import Any
import uuid

from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlmodel import Field, SQLModel, Column, DateTime, func, CheckConstraint, PrimaryKeyConstraint, ForeignKey

from joby.settings import get_settings


joby_settings = get_settings()


class TodoTask(SQLModel, table=True):
    __tablename__ = "joby_todo_task"
    __table_args__ = (CheckConstraint("created_at <= updated_at"),)

    id: uuid.UUID | None = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    created_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )
    name: str = Field(nullable=False)
    kwargs: dict[str, Any] = Field(sa_column=Column(JSONB), nullable=False)
    todo_at: datetime.datetime | None = Field(sa_column=Column(DateTime(timezone=True), default=None, nullable=True))
    done_at: datetime.datetime | None = Field(sa_column=Column(DateTime(timezone=True), default=None, nullable=True))
    max_retry_on_failure: int | None = Field(default=joby_settings.max_retry_on_failure, nullable=True)

    @classmethod
    async def _get_next():
        return 5


class TodoTaskParent(SQLModel, table=True):
    __tablename__ = "joby_todo_task_parents"
    __table_args__ = (PrimaryKeyConstraint("task_id", "parent_id"),)

    task_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("joby_todo_task.id", ondelete="CASCADE"), nullable=False)
    )
    parent_id: uuid.UUID | None = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("joby_todo_task.id", ondelete="CASCADE"), nullable=False)
    )
    root_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("joby_todo_task.id", ondelete="CASCADE"), nullable=False)
    )


class TodoTry(SQLModel, table=True):
    __tablename__ = "joby_todo_task_try"
    __table_args__ = (CheckConstraint("created_at <= updated_at"),)

    id: uuid.UUID | None = Field(sa_column=Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4))
    created_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )
    task_id: uuid.UUID = Field(
        sa_column=Column(UUID(as_uuid=True), ForeignKey("joby_todo_task.id", ondelete="CASCADE"), nullable=False)
    )
