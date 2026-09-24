from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.schemas import PromptRequest
from app.ai.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "ComicCraft AI is running"
    }


@router.post("/generate")
def generate_comic(request: PromptRequest):

    try:
        outline = generate_outline(
            story_prompt=request.story_prompt,
            character_name=request.character_name,
            setting=request.setting,
            tone=request.tone,
            art_style=request.art_style
        )

        story = generate_story(
            request,
            outline,
            request
        )

        generated_images = []

        for panel in outline:

            image_prompt = panel.get(
                "image_prompt",
                panel.get("scene_description", "")
            )

            image_path = generate_image(image_prompt)

            generated_images.append(image_path)

        comic_path = build_comic_layout(
            outline=outline,
            story=story,
            image_paths=generated_images
        )

        return {
            "success": True,
            "message": "Comic generated successfully",
            "outline": outline,
            "story": story,
            "images": generated_images,
            "comic": comic_path
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@router.post("/export/pdf")
def export_pdf():

    comic_id = "comiccraft_demo"
    title = "ComicCraft AI Comic"

    panels_dir = Path("static/panels")

    panels = []

    for i in range(1, 6):

        image_path = panels_dir / f"panel_{i}.png"

        print("Checking:", image_path)
        print("Exists:", image_path.exists())

        if image_path.exists():
            panels.append({
                "panel_number": i,
                "image_path": str(image_path)
            })

    print("TOTAL PANELS:", len(panels))

    layout = {
        "panels": panels
    }

    settings = {
        "art_style": "Comic Book",
        "tone": "Adventure"
    }

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