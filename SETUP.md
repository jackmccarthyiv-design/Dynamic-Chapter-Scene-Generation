# Setup Guide

## Prerequisites

### 1. System Requirements

- Python 3.9 or higher
- Blender 4.0 or higher
- ffmpeg (for video concatenation)
- 8GB+ RAM (16GB+ recommended for rendering)
- GPU recommended for Blender rendering (CUDA/OptiX support)

### 2. Install Blender

Download and install Blender from: https://www.blender.org/download/

**Linux:**
```bash
sudo snap install blender --classic
# or
sudo apt install blender
```

**macOS:**
```bash
brew install --cask blender
```

**Verify installation:**
```bash
blender --version
```

### 3. Install ffmpeg

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify installation:**
```bash
ffmpeg -version
```

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd Dynamic-Chapter-Scene-Generation
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download Spacy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required: Claude API key for chapter analysis
ANTHROPIC_API_KEY=your_key_here

# Optional: Path to Blender if not in PATH
BLENDER_PATH=/usr/bin/blender
```

**Get API Keys:**
- Anthropic API: https://console.anthropic.com/

### 6. Test Installation

```bash
python main.py --book examples/sample_chapter.txt --max-chapters 1 --no-render
```

This should analyze the sample chapter and generate a blueprint without rendering.

## Configuration

Edit `config.yaml` to customize:

- Video resolution and duration
- Blender render settings
- Scene generation parameters
- Available biomes, weather types, camera movements

## Usage

### Basic Usage

Process a complete book:

```bash
python main.py --book path/to/your_book.txt
```

### Testing

Process just a few chapters without rendering:

```bash
python main.py --book your_book.txt --max-chapters 3 --no-render
```

### With Rendering

Full pipeline with video generation:

```bash
python main.py --book your_book.txt --output ./my_output
```

### Custom Metadata

```bash
python main.py --book book.txt --title "Epic Fantasy" --genre "fantasy"
```

## Troubleshooting

### "Blender not found"

Set the full path in `.env`:
```bash
BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender
```

### "API key not found"

Make sure `.env` file exists and contains valid API key:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### Rendering is slow

1. Enable GPU rendering in Blender preferences
2. Reduce samples in `config.yaml`:
   ```yaml
   blender:
     samples: 64  # Lower = faster but noisier
   ```
3. Reduce resolution for testing

### Out of memory during rendering

- Reduce resolution in `config.yaml`
- Process fewer chapters at once with `--max-chapters`
- Increase system swap space

## Performance Tips

1. **For testing:** Use `--no-render` to skip video generation
2. **First run:** Process 1-3 chapters to verify everything works
3. **GPU acceleration:** Enable in Blender > Edit > Preferences > System
4. **Batch processing:** Process chapters in smaller batches if memory is limited

## Directory Structure

After setup, your directory should look like:

```
Dynamic-Chapter-Scene-Generation/
├── .env                    # Your API keys (do not commit!)
├── config.yaml            # Configuration
├── main.py               # CLI entry point
├── requirements.txt      # Python dependencies
├── src/                  # Source code
├── examples/             # Sample texts
├── output/              # Generated videos (created on first run)
└── data/                # Vector database (created on first run)
```

## Next Steps

1. Read `README.md` for conceptual overview
2. Try the sample chapter: `python main.py --book examples/sample_chapter.txt --no-render`
3. Process your own book!
4. Explore cross-book learning with `--find-patterns`
