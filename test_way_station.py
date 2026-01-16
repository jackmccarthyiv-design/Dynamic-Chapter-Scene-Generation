#!/usr/bin/env python3
"""Test scene rendering for the Way Station desert scene."""

import json
import re
from pathlib import Path

def parse_chapters(text: str):
    """Parse chapters from text."""
    pattern = r'^(?:Chapter|CHAPTER)\s+(\d+|[IVX]+)(?:\s*[:.\-]\s*(.+?))?$'
    lines = text.split('\n')
    chapters = []
    current_chapter = None
    current_title = None
    current_text = []

    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            if current_chapter is not None:
                chapters.append({
                    'number': current_chapter,
                    'title': current_title,
                    'text': '\n'.join(current_text).strip()
                })
            current_chapter = match.group(1)
            current_title = match.group(2)
            current_text = []
        else:
            if current_chapter is not None:
                current_text.append(line)

    if current_chapter is not None:
        chapters.append({
            'number': current_chapter,
            'title': current_title,
            'text': '\n'.join(current_text).strip()
        })

    return chapters


def generate_scene_blueprint(chapter_text: str, chapter_num: int = 1, title: str = None):
    """Generate a detailed scene blueprint based on chapter text analysis."""

    text_lower = chapter_text.lower()

    # Biome detection - more comprehensive
    biome_scores = {
        'desert_basin': sum([
            'desert' in text_lower,
            'sand' in text_lower,
            'dry' in text_lower,
            'heat' in text_lower,
            'sun' in text_lower,
            'dust' in text_lower,
            'bleached' in text_lower
        ]),
        'alpine_meadow': sum([
            'mountain' in text_lower,
            'peak' in text_lower,
            'pass' in text_lower,
            'alpine' in text_lower,
            'snow' in text_lower,
            'ice' in text_lower
        ]),
        'pine_forest': sum([
            'forest' in text_lower,
            'tree' in text_lower,
            'pine' in text_lower,
            'wood' in text_lower,
            'canopy' in text_lower
        ]),
        'coastal_cliff': sum([
            'coast' in text_lower,
            'ocean' in text_lower,
            'sea' in text_lower,
            'cliff' in text_lower,
            'wave' in text_lower
        ]),
        'urban_ruins': sum([
            'ruin' in text_lower,
            'building' in text_lower,
            'station' in text_lower,
            'stone' in text_lower,
            'wall' in text_lower,
            'door' in text_lower
        ]),
        'canyon': sum([
            'canyon' in text_lower,
            'ravine' in text_lower,
            'gorge' in text_lower
        ]),
        'grassland': sum([
            'plain' in text_lower,
            'grass' in text_lower,
            'meadow' in text_lower
        ])
    }
    biome = max(biome_scores, key=biome_scores.get)

    # Weather detection
    weather_cues = {
        'dust': 'dust' in text_lower or 'sand' in text_lower,
        'clear': 'sun' in text_lower and 'storm' not in text_lower,
        'mist': 'mist' in text_lower or 'fog' in text_lower,
        'wind': 'wind' in text_lower,
        'overcast': 'dim' in text_lower or 'gray' in text_lower,
        'storm': 'storm' in text_lower or 'rain' in text_lower
    }
    weather = 'dust' if weather_cues['dust'] else 'clear'
    for w, present in weather_cues.items():
        if present:
            weather = w
            break

    # Time of day detection
    if 'dawn' in text_lower or 'sunrise' in text_lower:
        time_of_day = 'dawn'
    elif 'dusk' in text_lower or 'sunset' in text_lower:
        time_of_day = 'dusk'
    elif 'night' in text_lower or 'moon' in text_lower:
        time_of_day = 'night'
    elif 'noon' in text_lower or 'midday' in text_lower:
        time_of_day = 'noon'
    elif 'golden' in text_lower:
        time_of_day = 'golden_hour'
    elif 'dim' in text_lower or 'slabs of sunlight' in text_lower:
        time_of_day = 'afternoon'
    else:
        time_of_day = 'afternoon'

    # Lighting detection
    lighting_cues = []
    if 'sunlight' in text_lower:
        lighting_cues.append('harsh sunlight')
    if 'dim' in text_lower:
        lighting_cues.append('dim interior light')
    if 'dust' in text_lower and ('hang' in text_lower or 'slabs' in text_lower):
        lighting_cues.append('dust motes in light shafts')
    if 'bleached' in text_lower:
        lighting_cues.append('bleaching sun')
    lighting = ', '.join(lighting_cues) if lighting_cues else 'diffuse ambient light'

    # Extract color palette from text
    palette = []
    color_mappings = {
        'pale': 'pale sand',
        'dry': 'bone white',
        'bleached': 'sun-bleached stone',
        'dust': 'dust gray',
        'wood': 'weathered wood brown',
        'heat': 'heat shimmer gold'
    }
    for word, color in color_mappings.items():
        if word in text_lower and len(palette) < 5:
            palette.append(color)
    if not palette:
        palette = ['sand beige', 'stone gray', 'dust brown', 'pale gold']

    # Extract motifs - visual elements
    motifs = []
    motif_mappings = {
        'stone building': ['building', 'station', 'structure'],
        'heavy wooden door': ['door'],
        'narrow windows': ['window'],
        'rough stone walls': ['wall', 'stone'],
        'counter': ['counter', 'slab'],
        'shelves and crates': ['shelves', 'crates'],
        'distant hills': ['hills', 'horizon'],
        'heat shimmer': ['heat', 'wobble']
    }
    for motif, keywords in motif_mappings.items():
        if any(kw in text_lower for kw in keywords):
            motifs.append(motif)

    # Camera suggestions
    if 'outside' in text_lower and 'inside' in text_lower:
        camera_movement = 'slow push-in from exterior to interior'
    elif 'threshold' in text_lower:
        camera_movement = 'slow approach and cross threshold'
    else:
        camera_movement = 'slow dolly forward'

    # Emotional proxy
    emotion_cues = []
    if 'survival' in text_lower:
        emotion_cues.append('survival instinct')
    if 'liminal' in text_lower or 'between' in text_lower:
        emotion_cues.append('liminality')
    if 'neutral' in text_lower:
        emotion_cues.append('neutrality')
    if 'fate' in text_lower or 'crossroads' in text_lower:
        emotion_cues.append('fateful crossroads')
    if 'listening' in text_lower or 'attentive' in text_lower:
        emotion_cues.append('watchful presence')
    if 'trade' in text_lower or 'business' in text_lower:
        emotion_cues.append('quiet transactions')
    emotional_proxy = ', '.join(emotion_cues) if emotion_cues else 'threshold between worlds'

    # Extract sensory details
    sensory_details = []
    if 'smell' in text_lower or 'scent' in text_lower:
        sensory_details.append('old smells: dry wood, cloth, stored food')
    if 'sound' in text_lower or 'hear' in text_lower or 'silence' in text_lower:
        sensory_details.append('weighted silence, occasional creaks')
    if 'dust' in text_lower:
        sensory_details.append('fine dust hanging in air')
    if 'heat' in text_lower:
        sensory_details.append('heat stored in stone')

    # Extract symbolic elements
    symbolic_elements = []
    if 'crossroads' in text_lower:
        symbolic_elements.append('crossroads - choice point')
    if 'fate' in text_lower:
        symbolic_elements.append('fate doing quiet business')
    if 'threshold' in text_lower:
        symbolic_elements.append('threshold between states')
    if 'neutral' in text_lower:
        symbolic_elements.append('neutral ground')
    if 'between' in text_lower:
        symbolic_elements.append('liminal space between moments')

    # Emotional arc
    if 'exposure' in text_lower and 'survival' in text_lower:
        emotional_arc = 'from exposure to shelter, not safety'
    elif 'emptiness' in text_lower and 'appears' in text_lower:
        emotional_arc = 'from emptiness to presence'
    else:
        emotional_arc = 'approach and discovery'

    # Build the comprehensive blueprint
    blueprint = {
        "chapter": chapter_num,
        "title": title or "Untitled Chapter",
        "scene_blueprint": {
            "biome": biome,
            "weather": weather,
            "time_of_day": time_of_day,
            "lighting": lighting,
            "palette": palette,
            "camera": {
                "angle": "eye level, slowly lowering to emphasize structure",
                "movement": camera_movement,
                "speed": "very slow, contemplative"
            },
            "motifs": motifs,
            "emotional_proxy": emotional_proxy,
            "continuity_anchors": [m for m in motifs[:3]],
            "transformation_from_previous": None,
            "raw_setting_cues": [
                "endless desert, featureless",
                "low stone building - the Way Station",
                "heavy wooden door",
                "narrow windows",
                "dim interior with dust motes",
                "old counter and shelves",
                "stone walls holding heat"
            ],
            "sensory_details": sensory_details,
            "symbolic_elements": symbolic_elements,
            "emotional_arc": emotional_arc
        },
        "blender_prompt": f"Render a {biome} landscape at {time_of_day} with {weather} conditions. "
                        f"Feature a solitary low stone building (Way Station) in the middle distance. "
                        f"The building has thick rough walls, a heavy wooden door, and narrow windows. "
                        f"Interior lighting suggests dim space with dust motes in shafts of light. "
                        f"Color palette: {', '.join(palette)}. "
                        f"Camera slowly approaches from exterior view. "
                        f"Atmosphere: desolate, liminal, pregnant with significance. "
                        f"No people visible. Subtle heat shimmer on horizon. "
                        f"Looping 10-second animation, cinematic quality."
    }

    return blueprint


def main():
    print("=" * 70)
    print("WAY STATION SCENE RENDERING TEST")
    print("=" * 70)

    # Load the scene
    scene_path = Path("examples/way_station_scene.txt")
    if not scene_path.exists():
        print(f"ERROR: Scene file not found at {scene_path}")
        return

    text = scene_path.read_text()

    # Parse chapters
    print("\n[1] PARSING SCENE")
    print("-" * 40)
    chapters = parse_chapters(text)
    print(f"Chapters found: {len(chapters)}")

    for ch in chapters:
        words = len(ch['text'].split())
        print(f"  Chapter {ch['number']}: {ch['title']}")
        print(f"    Word count: {words}")

    # Generate blueprint
    print("\n[2] GENERATING SCENE BLUEPRINT")
    print("-" * 40)

    chapter = chapters[0]
    blueprint = generate_scene_blueprint(
        chapter['text'],
        chapter_num=int(chapter['number']),
        title=chapter['title']
    )

    print(f"Biome detected: {blueprint['scene_blueprint']['biome']}")
    print(f"Weather: {blueprint['scene_blueprint']['weather']}")
    print(f"Time of day: {blueprint['scene_blueprint']['time_of_day']}")
    print(f"Lighting: {blueprint['scene_blueprint']['lighting']}")
    print(f"Palette: {blueprint['scene_blueprint']['palette']}")
    print(f"Motifs: {blueprint['scene_blueprint']['motifs']}")
    print(f"Emotional proxy: {blueprint['scene_blueprint']['emotional_proxy']}")
    print(f"Symbolic elements: {blueprint['scene_blueprint']['symbolic_elements']}")
    print(f"Emotional arc: {blueprint['scene_blueprint']['emotional_arc']}")

    # Save blueprint
    print("\n[3] SAVING BLUEPRINT")
    print("-" * 40)

    output_dir = Path("output/way_station_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    blueprint_path = output_dir / "scene_blueprint.json"
    blueprint_path.write_text(json.dumps(blueprint, indent=2))
    print(f"Blueprint saved to: {blueprint_path}")

    # Print full blueprint
    print("\n[4] FULL BLUEPRINT")
    print("-" * 40)
    print(json.dumps(blueprint, indent=2))

    # Print Blender prompt
    print("\n[5] BLENDER RENDERING PROMPT")
    print("-" * 40)
    print(blueprint['blender_prompt'])

    print("\n" + "=" * 70)
    print("SCENE ANALYSIS COMPLETE")
    print("=" * 70)

    return blueprint


if __name__ == "__main__":
    main()
