import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.api import api
from backend.database import init_db

STATIC_PATH = os.environ.get(
    "STATIC_PATH", os.path.join(os.path.dirname(__file__), "static")
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url="/api/docs",  # Move Swagger UI to /api/docs to avoid conflict with frontend /docs route
    redoc_url="/api/redoc",  # Move ReDoc to /api/redoc
    openapi_url="/api/openapi.json",
)

# CORS allowlist. Auth is a Bearer token in a header, not a cookie, so
# credentials are not needed -- and the wildcard-plus-credentials combination
# browsers reject outright is gone. Defaults to the production origin; set
# CORS_ORIGINS to a comma-separated list to allow more.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ORIGINS", "https://kanban.pearachute.com"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists(STATIC_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

app.include_router(api, prefix="/api")

# Serve documentation content files from docs/
CONTENT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs")


@app.get("/docs/{path:path}")
async def docs_handler(path: str):
    """Serve docs: .md files serve raw markdown, clean URLs serve SPA."""
    if path.endswith(".md"):
        # Serve the markdown file
        file_path = os.path.join(CONTENT_PATH, path)
        if os.path.exists(file_path):
            return FileResponse(file_path)

    # Clean URL or missing file → serve SPA
    index_path = os.path.join(STATIC_PATH, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Kanban API is running"}


@app.get("/")
async def root():
    index_path = os.path.join(STATIC_PATH, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Kanban API is running. Build the frontend to serve it here."}


@app.get("/{path:path}")
async def catch_all(path: str):
    """Serve index.html for all non-API, non-docs routes (SPA fallback)"""
    # Anything under /api/ reaching the fallback is an endpoint that does not
    # exist, and the SPA is the wrong answer for it: a 200 of HTML makes a
    # client's response.json() fail with a decode error rather than see a 404,
    # and makes a typo'd URL look like a working endpoint when probed by hand.
    # This is what produced the bad evidence in the auth-inconsistency report.
    if path == "api" or path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")

    index_path = os.path.join(STATIC_PATH, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Kanban API is running"}
