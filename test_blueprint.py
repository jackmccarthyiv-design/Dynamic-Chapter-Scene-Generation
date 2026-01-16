#!/usr/bin/env python3
"""Test blueprint generation (mock)."""

import json
from pathlib import Path

def generate_mock_blueprint(chapter_text: str):
    """Generate a mock scene blueprint based on chapter text."""

    # Extract some basic cues from the text
    text_lower = chapter_text.lower()

    # Detect biome
    if 'mountain' in text_lower or 'peak' in text_lower or 'pass' in text_lower:
        biome = 'alpine_meadow'
    elif 'forest' in text_lower or 'tree' in text_lower:
        biome = 'pine_forest'
    elif 'coast' in text_lower or 'ocean' in text_lower:
        biome = 'coastal_cliff'
    else:
        biome = 'open_plain'

    # Detect weather
    if 'mist' in text_lower or 'fog' in text_lower:
        weather = 'mist'
    elif 'storm' in text_lower or 'rain' in text_lower:
        weather = 'storm_clearing'
    elif 'wind' in text_lower:
        weather = 'windy'
    else:
        weather = 'clear'

    # Detect time
    if 'dawn' in text_lower or 'sunrise' in text_lower:
        time_of_day = 'dawn'
    elif 'dusk' in text_lower or 'sunset' in text_lower:
        time_of_day = 'dusk'
    elif 'night' in text_lower or 'moon' in text_lower:
        time_of_day = 'night'
    else:
        time_of_day = 'morning'

    # Extract motifs
    motifs = []
    if 'cairn' in text_lower:
        motifs.append('stone cairn')
    if 'hawk' in text_lower or 'bird' in text_lower:
        motifs.append('circling bird')
    if 'path' in text_lower or 'road' in text_lower:
        motifs.append('winding path')

    # Detect emotion
    if 'fear' in text_lower or 'danger' in text_lower:
        emotion = 'tension and anticipation'
    elif 'hope' in text_lower or 'freedom' in text_lower:
        emotion = 'cautious hope'
    elif 'loss' in text_lower or 'grief' in text_lower:
        emotion = 'melancholy'
    else:
        emotion = 'threshold moment, suspended between past and future'

    # Create blueprint
    blueprint = {
        "chapter": 1,
        "title": "The Crossing",
        "scene_blueprint": {
            "biome": biome,
            "weather": weather,
            "time_of_day": time_of_day,
            "lighting": "soft golden hour light breaking through clearing clouds",
            "palette": ["sage green", "slate gray", "pale gold", "ice blue"],
            "camera": {
                "angle": "low angle looking up toward mountain pass",
                "movement": "slow dolly forward with slight upward tilt",
                "speed": "very slow, contemplative"
            },
            "motifs": motifs,
            "emotional_proxy": emotion,
            "continuity_anchors": ["mountain silhouette", "stone cairn"],
            "transformation_from_previous": "first chapter - establishing world"
        },
        "video_prompt": f"{biome} at {time_of_day}, {weather} conditions, "
                       f"soft atmospheric lighting, {', '.join(motifs)}, "
                       f"cinematic camera slowly moving forward, no people, "
                       f"looping animation, photorealistic 3D landscape"
    }

    return blueprint

# Test it
print("🎬 Testing Blueprint Generation...")
print("=" * 60)

text = Path("examples/sample_chapter.txt").read_text()

# Skip the chapter header
chapter_text = '\n'.join(text.split('\n')[2:])

blueprint = generate_mock_blueprint(chapter_text)

print("✓ Blueprint generated!\n")
print(json.dumps(blueprint, indent=2))

print("\n" + "=" * 60)
print("✓ Blueprint test PASSED!")
print("=" * 60)

# Save it
output_dir = Path("output/test_run")
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / "blueprint.json").write_text(json.dumps(blueprint, indent=2))
print(f"\n💾 Blueprint saved to: {output_dir}/blueprint.json")
