import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


@app.get("/api/debug/docs-path")
async def debug_docs_path():
    """Debug endpoint to check docs path configuration."""
    from pathlib import Path

    content_path = str(Path(__file__).parent.parent / "docs")
    return {
        "content_path": content_path,
        "exists": os.path.exists(content_path),
        "files": os.listdir(content_path) if os.path.exists(content_path) else [],
    }


@app.get("/{path:path}")
async def catch_all(path: str):
    """Serve index.html for all non-API, non-docs routes (SPA fallback)"""
    index_path = os.path.join(STATIC_PATH, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Kanban API is running"}
