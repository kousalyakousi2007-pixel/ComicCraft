import os
from pathlib import Path

from huggingface_hub import InferenceClient

from app.config import PANELS_DIR, IMAGE_WIDTH, IMAGE_HEIGHT


def generate_image(prompt: str) -> str:

    if not prompt:
        raise ValueError("Image prompt cannot be empty.")

    token = os.getenv("HF_API_KEY")

    if not token:
        raise ValueError("HF_API_KEY is missing in .env")

    output_dir = Path(PANELS_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    existing_panels = list(output_dir.glob("panel_*.png"))
    panel_number = len(existing_panels) + 1

    output_file = output_dir / f"panel_{panel_number}.png"

    client = InferenceClient(
        api_key=token,
        provider="auto"
    )

    image = client.text_to_image(
        prompt=prompt,
        model="black-forest-labs/FLUX.1-schnell"
    )

    image = image.resize(
        (IMAGE_WIDTH, IMAGE_HEIGHT)
    )

    image.save(output_file)

    print(f"AI IMAGE CREATED: {output_file}")

    return str(output_file)