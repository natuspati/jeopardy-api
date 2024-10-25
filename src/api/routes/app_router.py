"""Routes module."""

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from api.routes.v1 import api_v1_router
from api.routes.websocket import ws_router
from exceptions.responses import INTERNAL_ERROR_RESPONSE, generate_responses

api_router = APIRouter(prefix="/api")
api_router.include_router(router=api_v1_router)

app_router = APIRouter()
app_router.include_router(router=api_router)
app_router.include_router(router=ws_router)


@app_router.get(
    "/",
    response_class=RedirectResponse,
    responses=generate_responses(INTERNAL_ERROR_RESPONSE),
)
async def index_page(request: Request):
    """
    Redirect to docs page.

    :return: redirect to docs page.
    """
    return RedirectResponse(url=request.app.docs_url)
