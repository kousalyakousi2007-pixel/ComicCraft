import json
import time

from google import genai

from app.config import (
    GEMINI_API_KEY,
    GEMINI_OUTLINE_MODEL,
    NUM_PANELS,
)


def generate_content(prompt: str):
    """
    Generate text using Gemini.

    If Gemini is temporarily unavailable (503),
    use a local fallback so the application can still
    be tested.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing in the .env file."
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    last_error = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=GEMINI_OUTLINE_MODEL,
                contents=prompt,
            )

            if response.text:
                return response.text

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        except Exception as error:

            last_error = error

            if "503" not in str(error) and "429" not in str(error):
                raise

            if attempt < 2:
                time.sleep(2 ** attempt)

    print(
        "Gemini is temporarily unavailable."
    )

    print(
        f"Gemini error: {last_error}"
    )

    return _fallback_outline()


def _fallback_outline():

    panels = []

    for i in range(1, NUM_PANELS + 1):

        panels.append(
            {
                "panel_number": i,
                "title": f"Adventure Panel {i}",
                "scene_description": (
                    f"The main character continues "
                    f"the adventure in panel {i}."
                ),
                "image_prompt": (
                    "Comic book illustration of a "
                    "college student discovering a "
                    "magical AI computer in a Chennai "
                    "college laboratory. Adventure "
                    "theme, detailed comic book art."
                ),
            }
        )

    return json.dumps(panels)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
):

    prompt = f"""
You are a professional comic book story planner.

Create exactly {NUM_PANELS} connected comic panels.

Story:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return ONLY valid JSON.

Format:

[
    {{
        "panel_number": 1,
        "title": "Panel title",
        "scene_description": "Scene description",
        "image_prompt": "Detailed image prompt"
    }}
]

Requirements:

1. Create exactly {NUM_PANELS} panels.
2. Keep the character consistent.
3. Make the story flow from beginning to ending.
4. Give a detailed image prompt for every panel.
"""

    text = generate_content(prompt)

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:

        data = json.loads(text)

    except json.JSONDecodeError as error:

        raise ValueError(
            "Gemini returned invalid JSON."
        ) from error

    if not isinstance(data, list):

        raise ValueError(
            "Gemini did not return a panel list."
        )

    if len(data) != NUM_PANELS:

        raise ValueError(
            f"Expected {NUM_PANELS} panels, "
            f"but Gemini returned {len(data)}."
        )

    return data