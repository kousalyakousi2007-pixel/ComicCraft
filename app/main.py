from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="AI-powered comic story and illustration generator",
    version="1.0.0"
)


STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=STATIC_DIR),
        name="static"
    )


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "ComicCraft AI is running!",
        "status": "success",
        "application": "ComicCraft"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "ComicCraft"
    }