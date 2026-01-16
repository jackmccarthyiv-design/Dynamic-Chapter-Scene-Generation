"""Data models for scene blueprints and chapter analysis."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CameraConfig(BaseModel):
    """Camera configuration for scene."""
    angle: str = Field(description="Camera angle (e.g., 'wide shot, low angle')")
    movement: str = Field(description="Camera movement type (e.g., 'slow pan left')")


class SceneBlueprint(BaseModel):
    """Complete scene blueprint for a chapter."""
    chapter: int
    title: Optional[str] = None

    # Core scene elements
    biome: str = Field(description="Primary biome/environment type")
    weather: str = Field(description="Weather conditions")
    time_of_day: str = Field(description="Time of day")
    lighting: str = Field(description="Lighting description")
    palette: List[str] = Field(description="Color palette for the scene")

    # Camera and framing
    camera: CameraConfig

    # Narrative elements
    motifs: List[str] = Field(description="Visual motifs and recurring objects")
    emotional_proxy: str = Field(description="Emotional state the landscape represents")

    # Continuity tracking
    continuity_anchors: List[str] = Field(default_factory=list, description="Elements that connect to other chapters")
    transformation_from_previous: Optional[str] = Field(default=None, description="How this scene transforms from the previous chapter")

    # Generated prompt
    blender_prompt: Optional[str] = Field(default=None, description="Detailed prompt for Blender scene generation")

    # Extracted metadata
    raw_setting_cues: List[str] = Field(default_factory=list)
    sensory_details: List[str] = Field(default_factory=list)
    symbolic_elements: List[str] = Field(default_factory=list)
    emotional_arc: Optional[str] = Field(default=None)


class ChapterData(BaseModel):
    """Parsed chapter data."""
    chapter_number: int
    title: Optional[str] = None
    text: str
    word_count: int


class BookMetadata(BaseModel):
    """Metadata about the processed book."""
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    total_chapters: int
    total_words: int
    processing_timestamp: str


class SceneGenerationResult(BaseModel):
    """Result of scene generation."""
    chapter: int
    blueprint: SceneBlueprint
    blend_file_path: Optional[str] = None
    video_path: Optional[str] = None
    success: bool
    error_message: Optional[str] = None
    generation_time: float = 0.0


class TransitionConfig(BaseModel):
    """Configuration for chapter-to-chapter transition."""
    from_chapter: int
    to_chapter: int
    transition_type: str = Field(description="escalation, revelation, descent, etc.")
    duration: float = Field(default=2.0, description="Transition duration in seconds")
    shared_anchors: List[str] = Field(default_factory=list)
    morph_elements: Dict[str, Any] = Field(default_factory=dict)
