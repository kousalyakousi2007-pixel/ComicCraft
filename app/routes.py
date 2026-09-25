from pathlib import Path
import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas import PromptRequest
from app.ai.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


router = APIRouter()

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "ComicCraft AI is running"
    }


# ---------------------------------------------------------
# HOME PAGE
# ---------------------------------------------------------

@router.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )


# ---------------------------------------------------------
# GENERATE COMIC
# ---------------------------------------------------------

@router.post("/generate")
async def generate_comic(request: Request):

    try:

        # -------------------------------------------------
        # READ REQUEST DATA
        # -------------------------------------------------

        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:

            data = await request.json()

            prompt_request = PromptRequest(**data)

            return_json = True

        else:

            form = await request.form()

            prompt_request = PromptRequest(
                story_prompt=form.get("story_prompt", ""),
                character_name=form.get("character_name", ""),
                setting=form.get("setting", ""),
                tone=form.get("tone", ""),
                art_style=form.get("art_style", "")
            )

            return_json = False


        # -------------------------------------------------
        # VALIDATE INPUT
        # -------------------------------------------------

        if not prompt_request.story_prompt:
            raise HTTPException(
                status_code=400,
                detail="Story prompt is required"
            )


        # -------------------------------------------------
        # GENERATE OUTLINE
        # -------------------------------------------------

        outline = generate_outline(
            story_prompt=prompt_request.story_prompt,
            character_name=prompt_request.character_name,
            setting=prompt_request.setting,
            tone=prompt_request.tone,
            art_style=prompt_request.art_style
        )


        # -------------------------------------------------
        # GENERATE STORY + DIALOGUE
        # -------------------------------------------------

        story = generate_story(
            prompt_request,
            outline,
            prompt_request
        )


        # -------------------------------------------------
        # PARSE STORY
        # -------------------------------------------------

        story_data = {}

        if isinstance(story, str):

            try:

                cleaned_story = story.strip()

                if cleaned_story.startswith("```json"):
                    cleaned_story = cleaned_story[7:]

                if cleaned_story.endswith("```"):
                    cleaned_story = cleaned_story[:-3]

                story_data = json.loads(
                    cleaned_story.strip()
                )

            except Exception:

                story_data = {}


        story_panels = story_data.get(
            "panels",
            []
        )


        # -------------------------------------------------
        # GENERATE IMAGES
        # -------------------------------------------------

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


        # -------------------------------------------------
        # BUILD COMIC LAYOUT
        # -------------------------------------------------

        comic_path = build_comic_layout(
            outline=outline,
            story=story,
            image_paths=generated_images
        )


        # -------------------------------------------------
        # PREPARE FRONTEND LAYOUT
        # -------------------------------------------------

        layout = []

        for index, panel in enumerate(outline):

            dialogue = ""

            if index < len(story_panels):

                dialogue = story_panels[index].get(
                    "dialogue",
                    ""
                )


            image_path = generated_images[index]

            # Convert Windows path to browser URL
            image_name = Path(image_path).name

            web_image_path = (
                f"/static/panels/{image_name}"
            )


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

                    "image": web_image_path,

                    "image_path": image_path
                }
            )


        # -------------------------------------------------
        # JSON RESPONSE
        # -------------------------------------------------

        if return_json:

            return {
                "success": True,
                "message": "Comic generated successfully",
                "outline": outline,
                "story": story,
                "images": generated_images,
                "layout": layout,
                "comic": comic_path
            }


        # -------------------------------------------------
        # HTML RESPONSE
        # -------------------------------------------------

        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "layout": layout,
                "story": story
            }
        )


    except HTTPException:
        raise


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ---------------------------------------------------------
# EXPORT PDF
# ---------------------------------------------------------

@router.post("/export/pdf")
def export_pdf():

    comic_id = "comiccraft_demo"

    title = "ComicCraft AI Comic"

    panels_dir = BASE_DIR / "static" / "panels"

    panels = []


    # -----------------------------------------------------
    # FIND ALL GENERATED PANEL IMAGES
    # -----------------------------------------------------

    image_files = sorted(
        panels_dir.glob("panel_*.png"),
        key=lambda p: p.stat().st_mtime
    )


    # Take latest 5 images
    image_files = image_files[-5:]


    for index, image_path in enumerate(
        image_files,
        start=1
    ):

        panels.append(
            {
                "panel_number": index,
                "image_path": str(image_path)
            }
        )


    # -----------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------

    layout = {
        "panels": panels
    }


    # -----------------------------------------------------
    # SETTINGS
    # -----------------------------------------------------

    settings = {
        "art_style": "Comic Book",
        "tone": "Adventure"
    }


    # -----------------------------------------------------
    # CREATE PDF
    # -----------------------------------------------------

    pdf_path = save_pdf(
        comic_id,
        title,
        layout,
        settings
    )


    return {
        "success": True,
        "message": "PDF exported successfully",
        "pdf": str(pdf_path),
        "panels_found": len(panels)
    }


# ---------------------------------------------------------
# EXPORT SUCCESS PAGE
# ---------------------------------------------------------

@router.get(
    "/export-success",
    response_class=HTMLResponse
)
def export_success(request: Request):

    return templates.TemplateResponse(
        "export_success.html",
        {
            "request": request,
            "pdf": "output/comiccraft_demo.pdf"
        }
    )