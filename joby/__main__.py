# coding: utf-8
import typer
import asyncio

from loguru import logger
from sqlmodel.sql.expression import Select, SelectOfScalar

from . import __version__ as joby_version
from .joby import _exec_module
from .settings import get_settings

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)

dev_app = typer.Typer()
app.add_typer(dev_app, name="dev")

db_app = typer.Typer()
app.add_typer(db_app, name="db")


@app.command()
def version():
    print(f"Joby version: {joby_version}")


# @app.command()
# def setup_db():
#     """Setup the database according the environnment variables

#     TODO: migrate to alembic
#     """

#     async def run():
#         async with engine.begin() as conn:
#             await conn.run_sync(SQLModel.metadata.create_all)
#             res = await conn.execute(select(db.Version))
#             try:
#                 row = res.scalar_one()
#             except sqlalchemy.exc.NoResultFound:
#                 async with AsyncSession(engine) as session:
#                     row = db.Version()
#                     session.add(row)
#                     await session.commit()

#     asyncio.new_event_loop().run_until_complete(run())


@app.command()
def worker():
    """Run Joby worker"""
    loop = asyncio.new_event_loop()
    exit(1)
    loop.run_until_complete(check_db())

    joby_settings = get_settings()
    logger.opt(colors=True).info("<green>Booting Joby worker</green>")
    _exec_module(joby_settings.jobs_file_path)


@dev_app.command("generate-migration-file")
def db_generate_migration_file(message: str, autogenerate=typer.Option(True)):

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

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run())


if __name__ == "__main__":
    app()
