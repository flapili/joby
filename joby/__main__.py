# coding: utf-8
import sys
import typer
import logging

from loguru import logger
from sqlmodel import select
from sqlmodel.sql.expression import Select, SelectOfScalar

from joby.db import get_session

# from .joby import _exec_module
# from .settings import get_settings

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)


@app.callback()
def verbose_callback(verbose: bool = typer.Option(False, "--verbose", "-v")):
    logger.remove(0)
    logger.add(sys.stderr, level="DEBUG" if verbose else "INFO")


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


@app.command()
def version():
    from . import __version__ as joby_version

    """Print the current Joby version installed"""
    print(f"Joby version: {joby_version}")


@app.command()
def api():
    """TODO: implement uvicorn cli settings"""
    import uvicorn

    uvicorn.run("joby.api:app", log_config={"version": 1, "disable_existing_loggers": False})


@app.command()
def worker(check_db_version: bool = typer.Option(True, " /--skip-check-db-version")):
    import asyncio
    from pathlib import Path

    """Run Joby worker"""
    from sqlalchemy.future.engine import Connection

    from .db import engine
    from .models import db
    from .worker import do_todo_task_wrapper

    loop = asyncio.new_event_loop()
    if check_db_version:
        from alembic import config, script
        from alembic.runtime import migration

        def check_db(conn: Connection, cfg: config.Config):
            directory = script.ScriptDirectory.from_config(cfg)
            context = migration.MigrationContext.configure(conn)
            return set(context.get_current_heads()) == set(directory.get_heads())

        async def run_check_db():
            cfg = config.Config(config_args={"script_location": Path(__file__).resolve().parent / "alembic"})
            async with engine.begin() as conn:
                return await conn.run_sync(check_db, cfg)

        is_sync: bool = loop.run_until_complete(run_check_db())
        if is_sync is False:
            logger.critical("The database schema's is not sync with Joby schema's ! ABORTING !")
            raise typer.Exit(1)

        loop.run_until_complete(run_check_db())

    running_tasks = set()
    last_iteration = False

    async def produce_try():
        session = await get_session()
        while last_iteration is False:
            async with session.begin():
                stmt = select(db.TodoTask).limit(1)
                todo_task: db.TodoTask | None = await session.scalar(stmt)
                if todo_task is None:
                    print("none")
                    await asyncio.sleep(10)
                    continue

                # job = await get_job_from_db(...)
                # job_id = job.id
                # is_async = job.is_async
                # job_id = uuid.uuid4()
                # is_async = True
                # if is_async:
                #     task = asyncio.create_task(do_job(job_id=job_id))
                # else:
                #     # TODO: create t from run_in_executor
                #     ...
                task = asyncio.create_task(do_todo_task_wrapper(todo_task.copy()))
                running_tasks.add(task)
                task.add_done_callback(running_tasks.discard)
                await asyncio.sleep(1)

    try:
        loop.run_until_complete(produce_try())
    except KeyboardInterrupt:
        last_iteration = True
        print("stopping, press again CTRL + C to force stop")
        loop.run_until_complete(asyncio.gather(*running_tasks))
        print("bye bye")

    # loop.run_until_complete(run())

    # joby_settings = get_settings()
    # logger.opt(colors=True).info("<green>Booting Joby worker</green>")
    # _exec_module(joby_settings.jobs_file_path)


dev_app = typer.Typer()
app.add_typer(dev_app, name="dev", help="Commands related to joby development")


@dev_app.command("generate-migration-file")
def db_generate_migration_file(message: str, autogenerate=typer.Option(True)):
    """Generate migration file (only usefull while developing this package)"""
    import asyncio
    from pathlib import Path

    from alembic import config
    import alembic.command

    from .db import engine

    def run_upgrade(connection, cfg: config.Config):
        cfg.attributes["connection"] = connection
        alembic.command.revision(cfg, message=message, autogenerate=autogenerate)

    async def run():
        cfg = config.Config(config_args={"script_location": Path(__file__).resolve().parent / "alembic"})
        async with engine.begin() as conn:
            await conn.run_sync(run_upgrade, cfg)

    asyncio.new_event_loop().run_until_complete(run())


db_app = typer.Typer()
app.add_typer(db_app, name="db", help="TODO:")


@db_app.command("upgrade")
def db_upgrade(revision: str = "head"):
    """Upgrade to a later version"""
    import asyncio
    from pathlib import Path

    from alembic import config
    import alembic.command

    from .db import engine

    def run_upgrade(connection, cfg: config.Config):
        cfg.attributes["connection"] = connection
        alembic.command.upgrade(cfg, revision=revision)

    async def run():
        cfg = config.Config(config_args={"script_location": Path(__file__).resolve().parent / "alembic"})
        async with engine.begin() as conn:
            await conn.run_sync(run_upgrade, cfg)

    asyncio.new_event_loop().run_until_complete(run())


@db_app.command("downgrade")
def db_downgrade(revision: str):
    """Revert to a previous version"""
    import asyncio
    from pathlib import Path

    from alembic import config
    import alembic.command

    from .db import engine

    def run_upgrade(connection, cfg: config.Config):
        cfg.attributes["connection"] = connection
        alembic.command.downgrade(cfg, revision=revision)

    async def run():
        cfg = config.Config(config_args={"script_location": Path(__file__).resolve().parent / "alembic"})
        async with engine.begin() as conn:
            await conn.run_sync(run_upgrade, cfg)

    asyncio.new_event_loop().run_until_complete(run())


if __name__ == "__main__":
    app()
