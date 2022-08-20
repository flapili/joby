# coding: utf-8
import asyncio

from loguru import logger

from joby.models import db


async def do_todo_task_wrapper(todo_task: db.TodoTask):

    logger.info(f"handling task {todo_task.id}")
    await asyncio.sleep(2)
    logger.info(f"task {todo_task.id} done !")
