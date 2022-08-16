# coding: utf-8
import sys
import typer
import asyncio
import logging

from loguru import logger
from sqlmodel.sql.expression import Select, SelectOfScalar

from . import __version__ as joby_version
from .joby import _exec_module
from .settings import get_settings

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)


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
    """Print the current Joby version installed"""
    print(f"Joby version: {joby_version}")


@app.command()
def worker():
    """Run Joby worker"""
    # loop = asyncio.new_event_loop()
    return

    # loop.run_until_complete(check_db())
    # joby_settings = get_settings()
    # logger.opt(colors=True).info("<green>Booting Joby worker</green>")
    # _exec_module(joby_settings.jobs_file_path)


dev_app = typer.Typer()
app.add_typer(dev_app, name="dev", help="Commands related to joby development")


@dev_app.command("generate-migration-file")
def db_generate_migration_file(message: str, autogenerate=typer.Option(True)):
    """Generate migration file (only usefull while developing this package)"""
    from alembic import config
    import alembic.command

    from . import _root
    from .db import engine

    def run_upgrade(connection, cfg: config.Config):
        cfg.attributes["connection"] = connection
        alembic.command.revision(cfg, message=message, autogenerate=autogenerate)

    async def run():
        cfg = config.Config(config_args={"script_location": _root / "alembic"})
        async with engine.begin() as conn:
            await conn.run_sync(run_upgrade, cfg)

    asyncio.new_event_loop().run_until_complete(run())


db_app = typer.Typer()
app.add_typer(db_app, name="db", help="TODO:")


@db_app.command("upgrade")
def db_upgrade(revision: str):
    """Upgrade to a later version"""
    from alembic import config
    import alembic.command

    from . import _root
    from .db import engine

    def run_upgrade(connection, cfg: config.Config):
        cfg.attributes["connection"] = connection
        alembic.command.upgrade(cfg, revision=revision)

    async def run():
        cfg = config.Config(config_args={"script_location": _root / "alembic"})
        async with engine.begin() as conn:
            await conn.run_sync(run_upgrade, cfg)

    asyncio.new_event_loop().run_until_complete(run())


@db_app.command("downgrade")
def db_downgrade(revision: str):
    """Revert to a previous version"""
    from alembic import config
    import alembic.command

    from . import _root
    from .db import engine

    def run_upgrade(connection, cfg: config.Config):
        cfg.attributes["connection"] = connection
        alembic.command.downgrade(cfg, revision=revision)

    async def run():
        cfg = config.Config(config_args={"script_location": _root / "alembic"})
        async with engine.begin() as conn:
            await conn.run_sync(run_upgrade, cfg)

    asyncio.new_event_loop().run_until_complete(run())


if __name__ == "__main__":
    app()
