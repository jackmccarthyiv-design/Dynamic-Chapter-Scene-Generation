# Architecture Overview

## System Design

The Dynamic Chapter Scene Generation system follows a multi-stage pipeline architecture that transforms literary text into cinematic landscape videos.

```
┌─────────────┐
│  Book (txt) │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Book Parser       │  Splits text into structured chapters
│   (parsers/)        │  Detects chapter boundaries, titles
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Chapter Analyzer   │  LLM-based analysis (Claude API)
│  (analyzers/)       │  Extracts: setting, weather, mood,
└──────┬──────────────┘  symbolism, motifs, emotional arc
       │
       ▼
┌─────────────────────┐
│  Scene Blueprint    │  Structured JSON specification
│  (models.py)        │  Biome, palette, camera, lighting
└──────┬──────────────┘
       │
       ├───────────────────────────┐
       │                           │
       ▼                           ▼
┌─────────────────┐      ┌───────────────────┐
│  Vector Store   │      │ Blender Generator │
│  (database/)    │      │ (generators/)     │
│  Cross-book     │      │ Procedural 3D     │
│  learning       │      │ scene creation    │
└─────────────────┘      └────────┬──────────┘
                                  │
                                  ▼
                         ┌───────────────────┐
                         │  Video Renderer   │
                         │  (renderers/)     │
                         │  Blender → MP4    │
                         └────────┬──────────┘
                                  │
                                  ▼
                         ┌───────────────────┐
                         │  Transition       │
                         │  Analyzer         │
                         │  Chapter morphs   │
                         └────────┬──────────┘
                                  │
                                  ▼
                         ┌───────────────────┐
                         │  Full Film        │
                         │  Concatenated     │
                         │  landscape movie  │
                         └───────────────────┘
```

## Core Components

### 1. Data Models (`src/models.py`)

Pydantic models that define the data structures:

- **ChapterData**: Raw chapter text with metadata
- **SceneBlueprint**: Complete scene specification
  - Biome, weather, time of day
  - Color palette
  - Camera configuration
  - Motifs and emotional proxy
  - Continuity anchors
- **BookMetadata**: Book-level information
- **TransitionConfig**: How scenes morph between chapters

### 2. Parsers (`src/parsers/`)

**BookParser** (`book_parser.py`):
- Reads text files
- Detects chapter boundaries using regex patterns
- Handles various chapter numbering schemes (numeric, Roman numerals)
- Extracts chapter titles
- Validates chapter length

Supported patterns:
- "Chapter 1"
- "CHAPTER I"
- "1. The Beginning"
- Configurable minimum word count

### 3. Analyzers (`src/analyzers/`)

**ChapterAnalyzer** (`llm_analyzer.py`):
- Uses Claude API (Sonnet 4.5) for deep text analysis
- Three-level analysis:
  1. **Surface**: Setting, weather, time cues
  2. **Symbolic**: Metaphors, recurring motifs
  3. **Comparative**: How settings evolve across chapters
- Generates structured JSON blueprints
- Maintains continuity via previous chapter context

**TransitionAnalyzer** (`transition_analyzer.py`):
- Analyzes emotional/visual shifts between chapters
- Classifies transitions:
  - `escalation`: Tension increases
  - `revelation`: Truth revealed, clarity
  - `descent`: Loss, deterioration
  - `journey`: Physical movement
  - `stasis`: Minimal change
- Identifies shared anchors for visual continuity

### 4. Vector Database (`src/database/`)

**SceneVectorStore** (`vector_store.py`):
- ChromaDB for persistent storage
- Sentence transformers for embeddings
- Cross-book pattern learning:
  - "Fear + forest → dark twisted trees, heavy fog"
  - "Hope + mountain → clearing skies, golden light"
- Query similar scenes by emotion/biome
- Pattern insights for genre-specific visual languages

### 5. Generators (`src/generators/`)

**BlenderSceneGenerator** (`blender_scene.py`):
- Runs inside Blender's Python environment (bpy)
- Procedural 3D scene generation:
  - Terrain generation with noise-based displacement
  - Material creation from color palettes
  - Atmospheric effects (fog, volumetrics)
  - Motif object placement
  - Camera setup and animation
  - Lighting based on time of day
- Saves .blend files for rendering

Key features:
- Biome-specific terrain profiles
- Weather-driven atmosphere
- Seamless loop animation (keyframe interpolation)
- Camera movements (pan, tilt, dolly, orbit)

### 6. Renderers (`src/renderers/`)

**VideoRenderer** (`video_renderer.py`):
- Orchestrates Blender execution via subprocess
- Generates .blend files from blueprints
- Renders animations to MP4 (H.264)
- Creates transition videos with ffmpeg cross-fades
- Concatenates chapter videos into full film

Render pipeline:
1. Blueprint → JSON
2. Blender (background) → .blend file
3. Blender (render) → MP4
4. ffmpeg → transitions + concatenation

### 7. Pipeline (`src/pipeline.py`)

**LandscapeGenerationPipeline**:
- Main orchestrator
- Coordinates all components
- Progress tracking with Rich library
- Error handling and recovery
- Statistics and insights

Process flow:
1. Parse book
2. Analyze context
3. Generate all blueprints (with continuity)
4. Store in vector DB
5. Analyze transitions
6. Render videos (parallel-capable)
7. Create full film

## Data Flow

### Chapter Analysis

```
Text → LLM Prompt → Claude API → JSON → SceneBlueprint
                          ↓
                   Vector Embeddings
                          ↓
                    ChromaDB Store
```

### Video Generation

```
SceneBlueprint → JSON File
                    ↓
              Blender Script
                    ↓
           Procedural Scene (.blend)
                    ↓
              Blender Render
                    ↓
                MP4 Video
```

## Configuration

### Environment Variables (`.env`)

```bash
ANTHROPIC_API_KEY=<key>
BLENDER_PATH=/path/to/blender
CHROMA_PERSIST_DIR=./data/chroma_db
```

### Config File (`config.yaml`)

Defines available options for:
- Biomes (20+ types)
- Weather conditions
- Times of day
- Camera movements
- Render settings

## Key Algorithms

### 1. Chapter Boundary Detection

Multi-pattern regex matching with fallback:
- Try standard patterns
- Parse Roman numerals
- Validate minimum length
- Default to single chapter if no boundaries found

### 2. Continuity Tracking

Each blueprint references previous blueprint:
```python
blueprint = analyze_chapter(
    chapter=current,
    previous_blueprint=previous,  # ← Continuity
    book_context=context
)
```

LLM receives previous scene info to maintain:
- Visual anchors (objects that persist)
- Motif evolution
- Spatial consistency

### 3. Transition Classification

Heuristic-based emotion analysis:
```python
tension_words = ['fear', 'danger', 'threat']
positive_words = ['hope', 'joy', 'relief']

if not from_tense and to_tense:
    return 'escalation'
```

### 4. Procedural Terrain

Noise-based displacement in Blender:
```python
texture = CloudsTexture(scale=biome_scale)
displace_mod.texture = texture
displace_mod.strength = biome_strength
```

Biome-specific profiles:
- Alpine: high strength, medium scale
- Desert: low strength, large scale
- Canyon: very high strength, small scale

### 5. Seamless Loop Animation

Keyframe at start, middle, end:
```python
camera.keyframe(frame=1)        # Start
camera.rotate(angle)
camera.keyframe(frame=middle)   # Transform
camera.reset()
camera.keyframe(frame=end)      # Return to start
```

## Extension Points

### Adding New Biomes

1. Add to `config.yaml`:
   ```yaml
   biomes:
     - volcanic_field
   ```

2. Add terrain profile in `blender_scene.py`:
   ```python
   'volcanic_field': {
     'scale': 3.0,
     'strength': 12.0
   }
   ```

### Custom LLM Analysis

Extend `ChapterAnalyzer`:
```python
def analyze_chapter_advanced(self, chapter):
    # Add custom analysis logic
    # Call additional APIs
    # Enhance blueprint
    pass
```

### New Transition Types

Add to `TransitionAnalyzer.TRANSITION_TYPES`:
```python
'awakening': {
    'description': 'Sudden realization',
    'visual_cues': ['light burst', 'color saturation']
}
```

## Performance Considerations

### Bottlenecks

1. **LLM API calls**: Sequential, rate-limited
   - Cache blueprints to avoid re-analysis
   - Use haiku model for faster prototyping

2. **Blender rendering**: CPU/GPU intensive
   - Reduce samples for testing (128 → 64)
   - Lower resolution (1080p → 720p)
   - Parallel rendering possible with job queue

3. **Vector database**: Embedding generation
   - Uses lightweight model (MiniLM)
   - Batch embedding for efficiency

### Optimization Strategies

- **Blueprint-only mode**: Skip rendering for fast iteration
- **Chapter batching**: Process N chapters at a time
- **Render farm**: Distribute Blender jobs
- **Model selection**: Use Claude Haiku for speed, Sonnet for quality

## Error Handling

- Graceful fallback blueprints if analysis fails
- Retry logic for API calls
- Subprocess timeouts for Blender
- Progress preservation (incremental output)

## Future Architecture Considerations

1. **Job queue system** (Celery/RQ) for distributed rendering
2. **Web API** for remote processing
3. **Real-time preview** with lightweight renderer
4. **Plugin system** for custom analyzers/generators
5. **Streaming output** for progressive video generation
