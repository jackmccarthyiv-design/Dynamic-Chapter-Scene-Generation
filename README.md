# Dynamic Chapter Scene Generation

A cinematic AI system that transforms books into character-free landscape films. Each chapter becomes a procedurally generated 3D scene—a living backdrop where the world does the acting.

## Concept

Feed it a book. It reads each chapter, extracts place, weather, time, texture, mood, and motion. Then generates looping landscape videos where:
- Fear becomes fog that tightens
- Hope becomes light breaking through clouds
- Isolation becomes endless geometry: dunes, empty streets, open water

The character isn't shown—but the world admits someone passed through.

## Architecture

```
Book (text file)
    ↓
Chapter Parser → Structured chapters
    ↓
LLM Analyzer → Scene blueprints (JSON)
    ↓
Blender Generator → 3D procedural scenes
    ↓
Video Renderer → Looping landscape videos
    ↓
Transition Builder → Chapter-to-chapter morphs
```

## Features

- **Surface-level extraction**: Setting, weather, time of day
- **Symbolic analysis**: Metaphors, recurring motifs, emotional arcs
- **Comparative tracking**: How locations evolve across chapters
- **Cross-book learning**: Pattern recognition across multiple books
- **Seamless loops**: Perfect video loops for each chapter
- **World transitions**: Landscapes morph between chapters

## Installation

```bash
pip install -r requirements.txt
```

Requires Blender 4.0+ installed and accessible via command line.

## Usage

```bash
# Process a single book
python main.py --book path/to/book.txt --output ./output

# Process with custom settings
python main.py --book book.txt --output ./scenes --loop-duration 15 --resolution 1920x1080
```

## Output Structure

```
output/
├── book_metadata.json
├── chapter_01/
│   ├── blueprint.json
│   ├── scene.blend
│   ├── landscape_loop.mp4
│   └── ambient_audio.wav
├── chapter_02/
│   └── ...
└── full_film.mp4
```

## Scene Blueprint Schema

Each chapter generates a structured scene blueprint:

```json
{
  "chapter": 1,
  "title": "The Departure",
  "scene_blueprint": {
    "biome": "coastal cliff",
    "weather": "wind, mist",
    "time_of_day": "blue hour",
    "lighting": "soft dusk glow",
    "palette": ["deep blue", "slate gray", "warm orange"],
    "camera": {
      "angle": "wide shot, low angle",
      "movement": "slow pan left"
    },
    "motifs": ["lighthouse", "rocky outcrop", "distant horizon"],
    "emotional_proxy": "departure, uncertainty",
    "continuity_anchors": ["lighthouse silhouette"],
    "transformation_from_previous": null
  }
}
```

## Cross-Book Learning

The system builds a vector database of chapter patterns:
- Grief + forest → dark, twisted trees, heavy fog
- Hope + mountain → clearing skies, golden light, expansive vista
- Tension + urban → narrow alleys, harsh shadows, claustrophobic framing

Over time, it learns genre-specific visual languages.
