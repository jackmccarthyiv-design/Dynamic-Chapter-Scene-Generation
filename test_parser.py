#!/usr/bin/env python3
"""Quick test of the book parser."""

from pathlib import Path
from src.parsers import BookParser
import json

def test_parser():
    """Test parsing the sample chapter."""
    print("Testing Book Parser...")
    print("-" * 50)

    parser = BookParser()
    book_path = Path("examples/sample_chapter.txt")

    if not book_path.exists():
        print(f"❌ Sample file not found: {book_path}")
        return

    # Parse the file
    chapters, metadata = parser.parse_file(book_path)

    print(f"✓ Book parsed successfully!")
    print(f"\nMetadata:")
    print(f"  Title: {metadata.title}")
    print(f"  Total chapters: {metadata.total_chapters}")
    print(f"  Total words: {metadata.total_words:,}")

    print(f"\nChapters:")
    for chapter in chapters:
        print(f"  Chapter {chapter.chapter_number}: {chapter.title or '(no title)'}")
        print(f"    Words: {chapter.word_count}")
        print(f"    Preview: {chapter.text[:100]}...")

    print("\n" + "=" * 50)
    print("✓ Parser test passed!")
    print("=" * 50)

if __name__ == "__main__":
    test_parser()
