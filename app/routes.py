from pathlib import Path
import json

from fastapi import APIRouter, HTTPException
from app.schemas import PromptRequest

from app.ai.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


router = APIRouter()


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
OUTPUT_DIR = BASE_DIR / "output"


# =========================================================
# HEALTH CHECK
# =========================================================

@router.get("/health")
def health_check():

    return {
        "status": "ok",
        "message": "ComicCraft AI is running"
    }


# =========================================================
# HOME
# =========================================================

@router.get("/")
def home():

    return {
        "message": "Welcome to ComicCraft AI",
        "status": "running",
        "application": "ComicCraft",
        "docs": "/docs",
        "health": "/health"
    }


# =========================================================
# HELPER - PARSE STORY
# =========================================================

def parse_story(story):

    if isinstance(story, dict):
        return story

    if not isinstance(story, str):
        return {}

    cleaned_story = story.strip()

    if cleaned_story.startswith("```json"):
        cleaned_story = cleaned_story[7:]

    elif cleaned_story.startswith("```"):
        cleaned_story = cleaned_story[3:]

    if cleaned_story.endswith("```"):
        cleaned_story = cleaned_story[:-3]

    cleaned_story = cleaned_story.strip()

    try:
        return json.loads(cleaned_story)

    except Exception:
        return {}


# =========================================================
# CREATE COMIC
# =========================================================

def create_comic(prompt_request: PromptRequest):

    # -----------------------------------------------------
    # Generate outline
    # -----------------------------------------------------

    outline = generate_outline(
        story_prompt=prompt_request.story_prompt,
        character_name=prompt_request.character_name,
        setting=prompt_request.setting,
        tone=prompt_request.tone,
        art_style=prompt_request.art_style
    )

    if not outline:
        raise Exception(
            "Comic outline generation failed."
        )


    # -----------------------------------------------------
    # Generate story and dialogue
    # -----------------------------------------------------

    story = generate_story(
        prompt_request,
        outline,
        prompt_request
    )

    story_data = parse_story(story)

    story_panels = story_data.get(
        "panels",
        []
    )


    # -----------------------------------------------------
    # Generate images
    # -----------------------------------------------------

    generated_images = []

    for panel in outline:

        image_prompt = panel.get(
            "image_prompt",
            panel.get(
                "scene_description",
                ""
            )
        )

        image_path = generate_image(
            image_prompt
        )

        generated_images.append(
            image_path
        )


    # -----------------------------------------------------
    # Build comic layout
    # -----------------------------------------------------

    comic_path = build_comic_layout(
        outline=outline,
        story=story,
        image_paths=generated_images
    )


    # -----------------------------------------------------
    # Prepare panel layout
    # -----------------------------------------------------

    layout = []

    for index, panel in enumerate(outline):

        dialogue = ""
        caption = ""
        narration = ""


        # Get story information
        if index < len(story_panels):

            current_story_panel = story_panels[index]

            if isinstance(
                current_story_panel,
                dict
            ):

                dialogue = current_story_panel.get(
                    "dialogue",
                    ""
                )

                caption = current_story_panel.get(
                    "caption",
                    ""
                )

                narration = current_story_panel.get(
                    "narration",
                    ""
                )


        # -------------------------------------------------
        # Image URL
        # -------------------------------------------------

        image_path = generated_images[index]

        image_name = Path(
            image_path
        ).name

        web_image_path = (
            f"/static/panels/{image_name}"
        )


        # -------------------------------------------------
        # Panel data
        # -------------------------------------------------

        layout.append(
            {
                "panel_number": panel.get(
                    "panel_number",
                    index + 1
                ),

                "title": panel.get(
                    "title",
                    f"Panel {index + 1}"
                ),

                "scene_description": panel.get(
                    "scene_description",
                    ""
                ),

                "dialogue": dialogue,

                "caption": caption,

                "narration": narration,

                "image": web_image_path,

                "image_path": str(
                    image_path
                )
            }
        )


    # -----------------------------------------------------
    # Return comic result
    # -----------------------------------------------------

    return {
        "outline": outline,
        "story": story,
        "story_data": story_data,
        "images": generated_images,
        "layout": layout,
        "comic": comic_path
    }


# =========================================================
# GENERATE COMIC
# =========================================================

@router.post("/generate")
def generate_comic(
    prompt_request: PromptRequest
):

    try:

        result = create_comic(
            prompt_request
        )

        return {
            "success": True,

            "message":
                "Comic generated successfully",

            "outline":
                result["outline"],

            "story":
                result["story"],

            "images":
                result["images"],

            "layout":
                result["layout"],

            "comic":
                result["comic"]
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# =========================================================
# EXPORT PDF
# =========================================================

@router.post("/export/pdf")
def export_pdf():

    try:

        comic_id = "comiccraft_demo"

        title = "ComicCraft AI Comic"


        # -------------------------------------------------
        # Check panels folder
        # -------------------------------------------------

        if not PANELS_DIR.exists():

            raise HTTPException(
                status_code=404,
                detail="Panels folder not found."
            )


        # -------------------------------------------------
        # Find generated images
        # -------------------------------------------------

        image_files = list(
            PANELS_DIR.glob(
                "panel_*.png"
            )
        )


        if not image_files:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No comic panel images found. "
                    "Generate a comic first."
                )
            )


        # -------------------------------------------------
        # Sort by modification time
        # -------------------------------------------------

        image_files = sorted(
            image_files,
            key=lambda p: p.stat().st_mtime
        )


        # Latest 5 images
        image_files = image_files[-5:]


        # -------------------------------------------------
        # Create panel list
        # -------------------------------------------------

        panels = []

        for index, image_path in enumerate(
            image_files,
            start=1
        ):

            panels.append(
                {
                    "panel_number": index,

                    "image_path": str(
                        image_path
                    )
                }
            )


        # -------------------------------------------------
        # Layout
        # -------------------------------------------------

        layout = {
            "panels": panels
        }


        # -------------------------------------------------
        # Settings
        # -------------------------------------------------

        settings = {

            "art_style":
                "Comic Book",

            "tone":
                "Adventure"
        }


        # -------------------------------------------------
        # Create PDF
        # -------------------------------------------------

        pdf_path = save_pdf(
            comic_id,
            title,
            layout,
            settings
        )


        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return {

            "success": True,

            "message":
                "PDF exported successfully",

            "pdf":
                str(pdf_path),

            "panels_found":
                len(panels)
        }


    except HTTPException:
        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )