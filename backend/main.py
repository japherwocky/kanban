import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

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

# Serve documentation content files
CONTENT_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "content")
if os.path.exists(CONTENT_PATH):
    app.mount("/content", StaticFiles(directory=CONTENT_PATH), name="content")


@app.get("/")
async def root():
    index_path = os.path.join(STATIC_PATH, "index.html")
    if os.path.exists(index_path):
        from fastapi.responses import FileResponse

        return FileResponse(index_path)
    return {"message": "Kanban API is running. Build the frontend to serve it here."}


@app.get("/{path:path}")
async def catch_all(path: str):
    """Serve index.html for all non-API routes (SPA fallback)"""
    index_path = os.path.join(STATIC_PATH, "index.html")
    if os.path.exists(index_path):
        from fastapi.responses import FileResponse

        return FileResponse(index_path)
    return {"message": "Kanban API is running"}
