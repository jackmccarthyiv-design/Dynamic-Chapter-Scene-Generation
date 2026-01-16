"""Dynamic Chapter Scene Generation - Transform books into cinematic landscape films."""

from .pipeline import LandscapeGenerationPipeline
from .models import (
    SceneBlueprint,
    ChapterData,
    BookMetadata,
    CameraConfig
)

__version__ = "0.1.0"

__all__ = [
    'LandscapeGenerationPipeline',
    'SceneBlueprint',
    'ChapterData',
    'BookMetadata',
    'CameraConfig'
]
