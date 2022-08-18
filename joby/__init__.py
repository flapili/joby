# coding: utf-8

from typing import Type
from pydantic import BaseModel

from .joby import Joby, get_default_joby

__version__ = "0.0.1"


def job(*, name: str, model: Type[BaseModel], joby: Joby | None = None, overwrite: bool = False):
    if joby is None:
        joby = get_default_joby()

    def decorator(job_func):
        joby.add_job(name=name, job_func=job_func, overwrite=overwrite, model=model)

    return decorator
