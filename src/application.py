import logging

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.routes import app_router
from exceptions.handlers import add_exception_handlers
from lifespan import lifespan
from settings import logging_settings, settings

logging.basicConfig(
    level=logging_settings.log_level.value,
    format=logging_settings.log_formatting,
    datefmt=logging_settings.date_formatting,
)

logger = logging.getLogger(__name__)


def get_app() -> FastAPI:
    """
    Create FastAPI application.

    This is the main constructor of the application.

    :return: FastAPI application
    """
    app = FastAPI(
        title=settings.service_name,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    add_exception_handlers(app)
    app.include_router(router=app_router)
    logger.info("Routing setup")

    app.add_websocket_route()

    return app
