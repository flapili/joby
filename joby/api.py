# coding: utf-8
import uuid
import datetime
from typing import Any

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from joby.db import get_session
from joby.models import db

app = FastAPI(title="Joby")


class TaskBody(BaseModel):
    name: str
    kwargs: dict[str, Any] = {}
    parent_ids: list[uuid.UUID] = []
    todo_at: datetime.datetime | None = None


async def get_root_id_from_db(task_id: uuid.UUID, session: AsyncSession) -> set[uuid.UUID]:
    """TODO:"""
    stmt = select(db.TodoTaskParent).where(db.TodoTaskParent.task_id == task_id)
    parent_relations: list[db.TodoTaskParent] = list(await session.scalars(stmt))
    if parent_relations:
        return set(relation.root_id for relation in parent_relations)
    return set([task_id])


@app.post("/task")
async def post_task(body: TaskBody, session: AsyncSession = Depends(get_session)):
    """Create a new task"""
    async with session.begin():
        root_ids: set[uuid.UUID] = set()
        for parent_id in body.parent_ids:
            root_ids = root_ids | await get_root_id_from_db(parent_id, session)

        if len(root_ids) > 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "more than 1 root detected", "root_ids": [str(x) for x in root_ids]},
            )

        new_todo_task = db.TodoTask(name=body.name, kwargs=body.kwargs, todo_at=body.todo_at)
        session.add(new_todo_task)
        await session.flush()
        todo_task_id = new_todo_task.id

        try:
            root_id = root_ids.pop()
        except KeyError:
            # there is no parents, the root task is the task itself
            root_id = todo_task_id

        for parent_id in body.parent_ids:
            session.add(db.TodoTaskParent(task_id=todo_task_id, parent_id=parent_id, root_id=root_id))
        await session.commit()
    return {"id": todo_task_id}
