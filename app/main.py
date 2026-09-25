from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from .routes import router


# ---------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


# ---------------------------------------------------------
# FASTAPI APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="AI-powered comic story and illustration generator",
    version="1.0.0"
)


# ---------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------

if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(STATIC_DIR)),
        name="static"
    )


# ---------------------------------------------------------
# ROOT ROUTE
# ---------------------------------------------------------

@app.get("/", include_in_schema=True)
async def root():
    return {
        "message": "Welcome to ComicCraft AI",
        "status": "running",
        "application": "ComicCraft",
        "docs": "/docs",
        "health": "/health"
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health", include_in_schema=True)
async def health_check():
    return {
        "status": "ok",
        "application": "ComicCraft"
    }


# ---------------------------------------------------------
# APPLICATION ROUTES
# ---------------------------------------------------------

app.include_router(router)