import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from backend.api import api
from backend.database import init_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_PATH = os.environ.get("STATIC_PATH", os.path.join(os.path.dirname(__file__), "static"))

if os.path.exists(STATIC_PATH):
    app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

app.include_router(api, prefix="/api")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
async def root():
    index_path = os.path.join(STATIC_PATH, "index.html")
    if os.path.exists(index_path):
        from fastapi.responses import FileResponse
        return FileResponse(index_path)
    return {"message": "Kanban API is running. Build the frontend to serve it here."}
