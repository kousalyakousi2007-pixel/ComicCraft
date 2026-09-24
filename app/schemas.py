from typing import List, Optional

from pydantic import BaseModel, Field


# =====================================================
# COMIC GENERATION REQUEST
# =====================================================

class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=1,
        description="Main story idea"
    )

    character_name: str = Field(
        ...,
        min_length=1,
        description="Main character name"
    )

    setting: str = Field(
        ...,
        min_length=1,
        description="Story setting"
    )

    tone: str = Field(
        default="Adventure",
        description="Story tone"
    )

    art_style: str = Field(
        default="Comic Book",
        description="Visual art style"
    )


# =====================================================
# COMIC PANEL
# =====================================================

class Panel(BaseModel):

    panel_number: int

    title: Optional[str] = ""

    scene_description: Optional[str] = ""

    image_prompt: Optional[str] = ""

    dialogue: Optional[str] = ""

    caption: Optional[str] = ""

    narration: Optional[str] = ""


# =====================================================
# OUTLINE RESPONSE
# =====================================================

class OutlineResponse(BaseModel):

    panels: List[Panel]


# =====================================================
# STORY RESPONSE
# =====================================================

class StoryResponse(BaseModel):

    panels: List[Panel]


# =====================================================
# COMIC RESPONSE
# =====================================================

class ComicResponse(BaseModel):

    success: bool

    message: str

    outline: Optional[object] = None

    story: Optional[object] = None

    images: List[str] = []

    comic: Optional[str] = None