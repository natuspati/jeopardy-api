"""Jeopardy application entry point."""

import uvicorn

from settings import logging_settings, settings


def main() -> None:
    """Entrypoint of the application."""
    uvicorn.run(
        "application:get_app",
        workers=settings.workers_count,
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_config=logging_settings.uvicorn_config,
        log_level=logging_settings.log_level.value.lower(),
        factory=True,
    )


if __name__ == "__main__":
    main()
