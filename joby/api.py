# coding: utf-8
import uuid
import datetime
from typing import Any

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from joby.db import get_session
from joby.models import db

app = FastAPI(title="Joby")


@app.get("/")
def read_root():
    return {"Hello": "World"}


class TaskBody(BaseModel):
    name: str
    kwargs: dict[str, Any] = {}
    parent_ids: list[uuid.UUID] = []
    todo_at: datetime.datetime | None = None


@app.post("/task")
async def post_task(body: TaskBody, session: AsyncSession = Depends(get_session)):
    async with session.begin():
        parent = await session.scalar(select(db.TodoTask).where(db.TodoTask.id == body.parent_ids[0]))
        print(parent)
        return
        todo_task = db.TodoTask(name=body.name, kwargs=body.kwargs, todo_at=body.todo_at)
        session.add(todo_task)
        await session.flush()
        todo_task_id = todo_task.id
        for parent_id in body.parent_ids:
            # TODO: use asyncio.gather
            # parent = await session.scalar(select())
            session.add(db.TodoTaskParent(task_id=todo_task_id, parent_id=parent_id))
        await session.commit()
    return {"id": todo_task_id}
