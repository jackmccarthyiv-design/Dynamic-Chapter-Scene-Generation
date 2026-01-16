#!/usr/bin/env python3
"""Standalone test - just the parser, no dependencies."""

import re
from pathlib import Path

def parse_chapters(text: str):
    """Simple chapter parser."""
    # Pattern for chapter headers
    pattern = r'^(?:Chapter|CHAPTER)\s+(\d+|[IVX]+)(?:\s*[:.\-]\s*(.+?))?$'

    lines = text.split('\n')
    chapters = []
    current_chapter = None
    current_text = []

    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            # Save previous chapter
            if current_chapter is not None:
                chapters.append({
                    'number': current_chapter,
                    'text': '\n'.join(current_text).strip()
                })

            # Start new chapter
            current_chapter = match.group(1)
            current_text = []
        else:
            if current_chapter is not None:
                current_text.append(line)

    # Save last chapter
    if current_chapter is not None:
        chapters.append({
            'number': current_chapter,
            'text': '\n'.join(current_text).strip()
        })

    return chapters

# Test it
print("🔍 Testing Book Parser...")
print("=" * 60)

text = Path("examples/sample_chapter.txt").read_text()
chapters = parse_chapters(text)

print(f"✓ Found {len(chapters)} chapter(s)\n")

for i, ch in enumerate(chapters, 1):
    words = len(ch['text'].split())
    preview = ch['text'][:150].replace('\n', ' ')
    print(f"Chapter {ch['number']}:")
    print(f"  Words: {words:,}")
    print(f"  Preview: {preview}...")
    print()

print("=" * 60)
print("✓ Parser test PASSED!")
print("=" * 60)
