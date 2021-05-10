"""Entry point to Zoyra."""
import pkg_resources

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from zorya.client.blueprints import api

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(
        directory=pkg_resources.resource_filename(__name__, "static/static")
    ),
    name="static",
)
app.include_router(api.router)


@app.get("/asset-manifest.json")
def asset_manifest():
    return FileResponse("static/asset-manifest.json")


@app.get("/manifest.json")
def manifest():
    return FileResponse("static/manifest.json")


@app.get("/service-worker.js")
def service_worker():
    return FileResponse("static/service-worker.js")


@app.get("/favicon.png")
def favicon():
    return FileResponse("static/favicon.png")


@app.get("/{catchall:path}")
def index():
    return FileResponse("static/index.html")
