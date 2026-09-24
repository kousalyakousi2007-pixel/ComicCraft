from app.ai.gemini_flash import generate_content


def generate_story(prompt_request, outline, settings):
    prompt = f"""
Create a detailed comic story based on this outline.

User prompt:
{prompt_request.story_prompt}


Outline:
{outline}

Return JSON in this format:
{{
    "panels": [
        {{
            "panel_number": 1,
            "dialogue": "..."
        }}
    ]
}}
"""

    return generate_content(prompt)