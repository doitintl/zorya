"""Entry point to Zoyra."""
import pkg_resources

from fastapi import FastAPI, responses, exceptions
from fastapi.staticfiles import StaticFiles

from zorya.server.routers import api
from zorya.server.routers import worker
from zorya.logging import Logger


app = FastAPI()

app.mount(
    "/static",
    StaticFiles(
        directory=pkg_resources.resource_filename(__name__, "static/static")
    ),
    name="static",
)
app.include_router(api.router)
app.include_router(worker.router)


@app.get("/asset-manifest.json")
def asset_manifest():
    return responses.FileResponse(
        pkg_resources.resource_filename(__name__, "static/asset-manifest.json")
    )


@app.get("/manifest.json")
def manifest():
    return responses.FileResponse(
        pkg_resources.resource_filename(__name__, "static/manifest.json")
    )


@app.get("/service-worker.js")
def service_worker():
    return responses.FileResponse(
        pkg_resources.resource_filename(__name__, "static/service-worker.js")
    )


@app.get("/favicon.png")
def favicon():
    return responses.FileResponse(
        pkg_resources.resource_filename(__name__, "static/favicon.png")
    )


@app.get("/{catchall:path}")
def index():
    return responses.FileResponse(
        pkg_resources.resource_filename(__name__, "static/index.html")
    )


@app.exception_handler(exceptions.RequestValidationError)
def log_all_exceptions(request, exception):
    Logger(request=request)(
        "request validation error",
        detail=exception.errors(),
        severity="ERROR",
    )
    return responses.JSONResponse(
        {"detail": exception.errors()}, status_code=422
    )
