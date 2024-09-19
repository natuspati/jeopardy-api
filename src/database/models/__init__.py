"""Database modules module."""

import importlib
import os
from pathlib import Path

from database.base_model import BaseDBModel


def import_models() -> list[type[BaseDBModel]]:  # noqa: WPS231, WPS210
    """
    Import all SQLAlchemy models.

    :return: list of SQLAlchemy models.
    """
    models_dir = Path(__file__).parent
    model_modules = []

    for file in os.listdir(models_dir):
        if file.endswith(".py") and file != "__init__.py":
            module_name = f"database.models.{file[:-3]}"  # noqa: WPS237
            module = importlib.import_module(module_name)

            # Get all classes from the module that are subclasses of BaseDBModel
            for attr_name in dir(module):  # noqa: WPS421
                attr = getattr(module, attr_name)
                if (  # noqa: WPS337
                    isinstance(attr, type)
                    and issubclass(attr, BaseDBModel)
                    and attr is not BaseDBModel
                ):
                    model_modules.append(attr)

    return model_modules


models = import_models()
