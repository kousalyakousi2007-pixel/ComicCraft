```python
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

STATIC_DIR = BASE_DIR / "static"

if STATIC_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=STATIC_DIR),
        name="static"
    )


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

app.include_router(router)


# ---------------------------------------------------------
# ROOT ROUTE
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "ComicCraft AI is running!",
        "status": "success",
        "application": "ComicCraft"
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "application": "ComicCraft"
    }
```
