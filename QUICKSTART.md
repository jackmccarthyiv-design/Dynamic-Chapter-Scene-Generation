# Quick Start Guide

Get up and running in 5 minutes.

## 1. Install Dependencies

```bash
# Install Blender (if not already installed)
sudo snap install blender --classic  # Linux
brew install --cask blender          # macOS

# Install ffmpeg
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # macOS

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## 2. Configure API Key

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get a key at: https://console.anthropic.com/

## 3. Test with Sample Chapter

```bash
# Generate blueprint only (fast, no rendering)
python main.py --book examples/sample_chapter.txt --no-render
```

This will:
- Parse the sample chapter
- Analyze it with Claude
- Generate a scene blueprint JSON
- Store patterns in vector database
- Skip video rendering

Output will be in: `./output/the_crossing_TIMESTAMP/`

## 4. View the Blueprint

```bash
# Find the most recent output directory
ls -lt output/ | head -2

# View the generated blueprint
cat output/the_crossing_*/chapter_01/blueprint.json
```

You should see a structured JSON with:
- Biome (e.g., "alpine_meadow")
- Weather, time of day, lighting
- Color palette
- Camera configuration
- Motifs and emotional proxy

## 5. Generate Your First Video (Optional)

If you want to test the full pipeline including video generation:

```bash
# Render the sample chapter (takes 5-10 minutes)
python main.py --book examples/sample_chapter.txt --max-chapters 1
```

This will:
- Generate blueprint
- Create Blender scene
- Render 10-second looping video
- Output: `./output/the_crossing_*/chapter_01/landscape_loop.mp4`

## 6. Process Your Own Book

```bash
# Prepare your book as a text file with clear chapter markers:
# Chapter 1
# Chapter text here...
#
# Chapter 2
# Chapter text here...

# Process it (blueprints only for testing)
python main.py --book /path/to/your_book.txt --max-chapters 5 --no-render

# Or full pipeline with rendering
python main.py --book /path/to/your_book.txt --max-chapters 5
```

## Common Commands

```bash
# Process full book (blueprints only)
python main.py --book book.txt --no-render

# Process with rendering
python main.py --book book.txt

# Process first 3 chapters only
python main.py --book book.txt --max-chapters 3

# Custom output directory
python main.py --book book.txt --output ./my_landscapes

# With metadata
python main.py --book book.txt --title "Epic Fantasy" --genre "fantasy"

# View database stats
python main.py --show-stats

# Find visual patterns for an emotion
python main.py --find-patterns "fear"
python main.py --find-patterns "hope"
```

## What Gets Created

After processing a book, you'll have:

```
output/your_book_TIMESTAMP/
├── book_metadata.json          # Book info
├── all_blueprints.json        # All chapter blueprints
├── transitions.json           # Chapter-to-chapter transitions
├── chapter_01/
│   ├── blueprint.json        # Scene specification
│   ├── scene.blend          # Blender file (if rendered)
│   └── landscape_loop.mp4   # Video loop (if rendered)
├── chapter_02/
│   └── ...
└── full_film.mp4             # All chapters concatenated
```

## Troubleshooting

**"ANTHROPIC_API_KEY not found"**
- Make sure `.env` exists and contains your key
- Try: `cat .env` to verify

**"Blender not found"**
- Check installation: `blender --version`
- Or set path in `.env`: `BLENDER_PATH=/usr/bin/blender`

**Rendering takes forever**
- Start with `--no-render` to test pipeline
- Reduce samples in `config.yaml`: `samples: 64`
- Use smaller resolution for testing

**Out of memory**
- Process fewer chapters: `--max-chapters 3`
- Use `--no-render` to skip video generation
- Close other applications

## Next Steps

1. Read `SETUP.md` for detailed configuration
2. Read `ARCHITECTURE.md` to understand the system
3. Read `README.md` for the full concept
4. Customize `config.yaml` for your preferences
5. Process your own books!

## Tips

- Always test with `--no-render` first to verify parsing/analysis
- Use `--max-chapters 1` to test a single chapter quickly
- The vector database learns from each book you process
- Use `--find-patterns` to explore what the system has learned
- Blueprint generation is fast (~30s per chapter)
- Video rendering is slow (~5-10 min per chapter, depending on hardware)

## Getting Help

- Check `SETUP.md` for common issues
- Review `ARCHITECTURE.md` to understand components
- Ensure all dependencies are installed correctly
- Verify API key is valid
- Try processing the sample chapter first

Happy landscape generation! 🎬🏔️
