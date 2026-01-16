"""LLM-based chapter analysis and scene blueprint generation."""

import json
import os
from typing import Optional, List
from anthropic import Anthropic
import yaml

from ..models import ChapterData, SceneBlueprint, CameraConfig


class ChapterAnalyzer:
    """Analyze chapters using LLM to generate scene blueprints."""

    SYSTEM_PROMPT = """You are a cinematic analysis AI trained to extract visual landscape elements from literary text.

Your task: Read a chapter and generate a character-free scene blueprint—a description of the WORLD where this chapter takes place, treating the environment as the protagonist.

Rules:
- NO characters, NO faces, NO people in the scene
- The landscape reflects what characters experience WITHOUT showing them
- Fear becomes fog that tightens
- Hope becomes light breaking through clouds
- Isolation becomes endless geometry

Extract:
1. SETTING: Biome, weather, time of day, lighting, color palette
2. SYMBOLIC: Metaphors, emotional proxies, recurring motifs
3. CAMERA: Angle, movement, framing
4. CONTINUITY: Elements that connect to previous chapters
5. TRANSFORMATION: How the world has changed since the last chapter

Output must be valid JSON matching the SceneBlueprint schema."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            config_path: Path to config.yaml
        """
        # Load configuration
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = {}

        # Initialize LLM client
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv('LLM_MODEL', 'claude-sonnet-4-5-20250929')

        # Load scene configuration options
        self.biomes = self.config.get('scene_generation', {}).get('biomes', [])
        self.weather_types = self.config.get('scene_generation', {}).get('weather_types', [])
        self.time_of_day = self.config.get('scene_generation', {}).get('time_of_day', [])
        self.camera_movements = self.config.get('scene_generation', {}).get('camera_movements', [])

    def analyze_chapter(
        self,
        chapter: ChapterData,
        previous_blueprint: Optional[SceneBlueprint] = None,
        book_context: Optional[str] = None
    ) -> SceneBlueprint:
        """
        Analyze a chapter and generate scene blueprint.

        Args:
            chapter: Chapter data to analyze
            previous_blueprint: Blueprint from previous chapter for continuity
            book_context: Optional context about the book (genre, themes)

        Returns:
            SceneBlueprint for the chapter
        """
        # Build the analysis prompt
        prompt = self._build_analysis_prompt(chapter, previous_blueprint, book_context)

        # Call LLM
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=self.SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse response
        response_text = response.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        json_text = self._extract_json(response_text)

        # Parse into blueprint
        blueprint_data = json.loads(json_text)

        # Ensure chapter number is set
        blueprint_data['chapter'] = chapter.chapter_number
        if 'title' not in blueprint_data or not blueprint_data['title']:
            blueprint_data['title'] = chapter.title

        # Generate Blender prompt
        blueprint_data['blender_prompt'] = self._generate_blender_prompt(blueprint_data)

        return SceneBlueprint(**blueprint_data)

    def _build_analysis_prompt(
        self,
        chapter: ChapterData,
        previous_blueprint: Optional[SceneBlueprint],
        book_context: Optional[str]
    ) -> str:
        """Build the complete analysis prompt."""
        prompt_parts = []

        if book_context:
            prompt_parts.append(f"BOOK CONTEXT:\n{book_context}\n")

        prompt_parts.append(f"CHAPTER {chapter.chapter_number}")
        if chapter.title:
            prompt_parts.append(f"Title: {chapter.title}")

        prompt_parts.append(f"\nCHAPTER TEXT:\n{chapter.text}\n")

        if previous_blueprint:
            prompt_parts.append(f"\nPREVIOUS CHAPTER SCENE:")
            prompt_parts.append(f"- Biome: {previous_blueprint.biome}")
            prompt_parts.append(f"- Weather: {previous_blueprint.weather}")
            prompt_parts.append(f"- Time: {previous_blueprint.time_of_day}")
            prompt_parts.append(f"- Motifs: {', '.join(previous_blueprint.motifs)}")
            prompt_parts.append(f"- Continuity anchors: {', '.join(previous_blueprint.continuity_anchors)}")

        prompt_parts.append(f"\nAVAILABLE OPTIONS:")
        prompt_parts.append(f"Biomes: {', '.join(self.biomes)}")
        prompt_parts.append(f"Weather: {', '.join(self.weather_types)}")
        prompt_parts.append(f"Time of day: {', '.join(self.time_of_day)}")
        prompt_parts.append(f"Camera movements: {', '.join(self.camera_movements)}")

        prompt_parts.append("""
Generate a scene blueprint as JSON with this structure:
{
  "biome": "string (e.g., 'coastal_cliff', 'pine_forest')",
  "weather": "string (e.g., 'mist', 'clearing storm')",
  "time_of_day": "string (e.g., 'dawn', 'blue_hour')",
  "lighting": "string (description of lighting quality)",
  "palette": ["color1", "color2", "color3"],
  "camera": {
    "angle": "string (e.g., 'wide shot, low angle')",
    "movement": "string (e.g., 'slow_pan_left', 'dolly_forward')"
  },
  "motifs": ["object1", "object2", "object3"],
  "emotional_proxy": "string (what emotion this landscape embodies)",
  "continuity_anchors": ["element1", "element2"],
  "transformation_from_previous": "string or null",
  "raw_setting_cues": ["quote1", "quote2"],
  "sensory_details": ["detail1", "detail2"],
  "symbolic_elements": ["symbol1", "symbol2"],
  "emotional_arc": "string (the emotional journey of this chapter)"
}

Remember: NO CHARACTERS. The world does the acting.""")

        return '\n'.join(prompt_parts)

    def _extract_json(self, text: str) -> str:
        """Extract JSON from LLM response, handling markdown code blocks."""
        # Try to find JSON in code blocks
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            return text[start:end].strip()
        elif '```' in text:
            start = text.find('```') + 3
            end = text.find('```', start)
            return text[start:end].strip()
        else:
            # Assume entire response is JSON
            return text.strip()

    def _generate_blender_prompt(self, blueprint_data: dict) -> str:
        """Generate a detailed Blender scene prompt from blueprint."""
        parts = []

        # Core scene description
        parts.append(f"{blueprint_data['biome']} landscape")
        parts.append(f"during {blueprint_data['time_of_day']}")
        parts.append(f"with {blueprint_data['weather']} weather")

        # Lighting and mood
        parts.append(f"{blueprint_data['lighting']}")

        # Color palette
        if blueprint_data.get('palette'):
            colors = ', '.join(blueprint_data['palette'])
            parts.append(f"color palette: {colors}")

        # Motifs
        if blueprint_data.get('motifs'):
            motifs = ', '.join(blueprint_data['motifs'])
            parts.append(f"featuring: {motifs}")

        # Camera
        camera = blueprint_data.get('camera', {})
        if camera:
            parts.append(f"camera: {camera.get('angle', 'wide shot')}")
            parts.append(f"movement: {camera.get('movement', 'static')}")

        # Style instructions
        parts.append("cinematic, atmospheric, no people, no characters")
        parts.append("photorealistic, detailed environment")
        parts.append(f"mood: {blueprint_data.get('emotional_proxy', 'neutral')}")

        return ', '.join(parts)

    def analyze_book_context(self, chapters: List[ChapterData]) -> str:
        """
        Analyze the overall book to extract context for chapter analysis.

        Args:
            chapters: All chapters in the book

        Returns:
            Context string about the book
        """
        # Use first chapter and last chapter for context
        first_chapter_preview = chapters[0].text[:1000] if chapters else ""
        last_chapter_preview = chapters[-1].text[:1000] if len(chapters) > 1 else ""

        prompt = f"""Analyze these excerpts from a book and provide:
1. Genre (fantasy, sci-fi, literary fiction, thriller, etc.)
2. Primary themes
3. Overall tone and atmosphere
4. Setting type (urban, rural, fantasy world, space, etc.)

First chapter excerpt:
{first_chapter_preview}

Last chapter excerpt:
{last_chapter_preview}

Provide a brief 2-3 sentence summary."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text.strip()
