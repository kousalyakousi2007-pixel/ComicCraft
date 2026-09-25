from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router


# ---------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

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
# APPLICATION ROUTES
# ---------------------------------------------------------

app.include_router(router)