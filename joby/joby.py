# coding: utf-8
import inspect
import importlib.util
from pathlib import Path
from typing import Any, Callable, Literal, Type

from loguru import logger
from pydantic import BaseModel


class Joby:
    def __init__(self, name: str = "default") -> None:
        self._name = name
        self._jobs = {}

    def add_job(
        self, *, name: str, job_func: Callable[..., Any], model=Type[BaseModel], overwrite: bool = False
    ) -> None:
        if name in self._jobs and overwrite is False:
            logger.opt(colors=True).warning(f"<yellow>Job [{name}] is already registered ! SKIPPING</yellow>")
        else:
            mode = "async" if inspect.iscoroutinefunction(job_func) else "process"
            job = Job(name=name, job_func=job_func, mode=mode, model=model, joby=self)
            logger.opt(colors=True).info(f"Registering [{job.name}] : {job}")
            self._jobs[name] = job
            logger.opt(colors=True).info(f"<green>[{job.name}] is now registered</green>")

    def remove_job(self, *, name: str) -> None:
        try:
            del self._jobs[name]
            logger.opt(colors=True).info(f"<green>[{name}] is now unregistered</green>")
        except KeyError:
            logger.warning(f"[{name}] is not registered ! SKIPPING")

    @property
    def name(self):
        return self._name

    @property
    def jobs(self):
        return self._jobs

    def __repr__(self) -> str:
        fields = {
            "name": self.name,
        }
        formatted_fields = ", ".join(f"<cyan>{k}</cyan>={v}" for k, v in fields.items())
        return "Joby({0})".format(formatted_fields)


class Job(BaseModel):
    name: str
    job_func: Callable[..., Any]
    mode: Literal["async", "process"]
    model: Type[BaseModel]
    joby: Joby

    def __str__(self) -> str:
        fields = {
            "name": self.name,
            "mode": self.mode,
        }
        formatted_fields = ", ".join(f"<cyan>{k}</cyan>={v}" for k, v in fields.items())
        return "Job({0})".format(formatted_fields)

    class Config:
        arbitrary_types_allowed = True


_default_joby = Joby()


def get_default_joby() -> Joby:
    return _default_joby


def _exec_module(path: Path) -> None:
    spec = importlib.util.spec_from_file_location(name=path.name, location=path)
    module = importlib.util.module_from_spec(spec=spec)
    spec.loader.exec_module(module=module)
