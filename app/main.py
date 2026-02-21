from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.database import init_db

app = FastAPI(title="Robi Studio Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


@app.get("/")
def root() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/student")
def student_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "pages" / "student.html")


@app.get("/parent")
def parent_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "pages" / "parent.html")


@app.get("/admin")
def admin_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "pages" / "admin.html")
