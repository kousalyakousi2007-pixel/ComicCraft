from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router


# ---------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent


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

app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static"
)


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

app.include_router(router)


# ---------------------------------------------------------
# ROOT HEALTH CHECK
# ---------------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "ComicCraft AI is running",
        "status": "success"
    } 
@app.get("/")
def root():
    return {
        "status": "success",
        "message": "ComicCraft AI is running"
    }
@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "application": "ComicCraft"
    }