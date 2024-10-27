from typing import Any

from fastapi import FastAPI, Request
from starlette.datastructures import URLPath


class RouteService:
    def __init__(self, request: Request):
        self._request = request
        self._app: FastAPI = request.app

    def get_route(self, name: str, **path_params: Any) -> URLPath:
        """
        Get route url with path parameters.

        :param name: route name
        :param path_params: path parameters
        :return: route url as string
        """
        return self._app.url_path_for(name, **path_params)
