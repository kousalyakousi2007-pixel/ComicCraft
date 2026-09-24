import os
from pathlib import Path

from dotenv import load_dotenv


# =====================================================
# BASE DIRECTORY
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# LOAD .ENV
# =====================================================

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# =====================================================
# GEMINI SETTINGS
# =====================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
)

GEMINI_OUTLINE_MODEL = os.getenv(
    "GEMINI_OUTLINE_MODEL",
    "gemini-1.5-flash"
)

GEMINI_STORY_MODEL = os.getenv(
    "GEMINI_STORY_MODEL",
    "gemini-1.5-pro"
)


# =====================================================
# HUGGING FACE SETTINGS
# =====================================================

HF_API_KEY = os.getenv(
    "HF_API_KEY",
    ""
)

HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "runwayml/stable-diffusion-v1-5"
)


# =====================================================
# IMAGE SETTINGS
# =====================================================

USE_LOCAL_DIFFUSERS = (
    os.getenv(
        "USE_LOCAL_DIFFUSERS",
        "false"
    ).lower() == "true"
)


IMAGE_WIDTH = int(
    os.getenv(
        "IMAGE_WIDTH",
        "768"
    )
)


IMAGE_HEIGHT = int(
    os.getenv(
        "IMAGE_HEIGHT",
        "768"
    )
)


# =====================================================
# COMIC SETTINGS
# =====================================================

NUM_PANELS = int(
    os.getenv(
        "NUM_PANELS",
        "5"
    )
)


# =====================================================
# DIRECTORIES
# =====================================================

STATIC_DIR = BASE_DIR / "static"

PANELS_DIR = STATIC_DIR / "panels"

EXPORTS_DIR = STATIC_DIR / "exports"


# =====================================================
# CREATE DIRECTORIES
# =====================================================

PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

EXPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)