"""Parse text files into structured chapter data."""

import re
from typing import List, Optional
from pathlib import Path

from ..models import ChapterData, BookMetadata
from datetime import datetime


class BookParser:
    """Parse text files and extract chapters."""

    # Common chapter heading patterns
    CHAPTER_PATTERNS = [
        r'^Chapter\s+(\d+)',  # Chapter 1
        r'^Chapter\s+([IVXLCDM]+)',  # Chapter I, II, III (Roman numerals)
        r'^(\d+)\.',  # 1.
        r'^CHAPTER\s+(\d+)',  # CHAPTER 1
        r'^\d+\.\s+(.+)$',  # 1. Title
    ]

    def __init__(self, min_chapter_length: int = 100):
        """
        Initialize parser.

        Args:
            min_chapter_length: Minimum word count for a valid chapter
        """
        self.min_chapter_length = min_chapter_length

    def parse_file(self, file_path: Path) -> tuple[List[ChapterData], BookMetadata]:
        """
        Parse a text file into chapters.

        Args:
            file_path: Path to the text file

        Returns:
            Tuple of (list of ChapterData, BookMetadata)
        """
        text = file_path.read_text(encoding='utf-8')

        # Try to detect chapter boundaries
        chapters = self._split_into_chapters(text)

        # Create metadata
        metadata = BookMetadata(
            title=self._extract_title(text),
            total_chapters=len(chapters),
            total_words=sum(c.word_count for c in chapters),
            processing_timestamp=datetime.now().isoformat()
        )

        return chapters, metadata

    def _split_into_chapters(self, text: str) -> List[ChapterData]:
        """Split text into chapters based on common patterns."""
        lines = text.split('\n')

        chapters = []
        current_chapter_lines = []
        current_chapter_num = 0
        current_title = None

        for line in lines:
            line_stripped = line.strip()

            # Check if this line is a chapter heading
            is_chapter_heading = False
            detected_num = None
            detected_title = None

            for pattern in self.CHAPTER_PATTERNS:
                match = re.match(pattern, line_stripped, re.IGNORECASE)
                if match:
                    is_chapter_heading = True
                    # Extract chapter number
                    if match.groups():
                        detected_num = self._parse_chapter_number(match.group(1))
                        if len(match.groups()) > 1:
                            detected_title = match.group(2).strip()
                    break

            if is_chapter_heading and current_chapter_lines:
                # Save previous chapter
                chapter_text = '\n'.join(current_chapter_lines).strip()
                if self._is_valid_chapter(chapter_text):
                    chapters.append(ChapterData(
                        chapter_number=current_chapter_num,
                        title=current_title,
                        text=chapter_text,
                        word_count=len(chapter_text.split())
                    ))

                # Start new chapter
                current_chapter_num = detected_num if detected_num else current_chapter_num + 1
                current_title = detected_title
                current_chapter_lines = []
            else:
                current_chapter_lines.append(line)

        # Add final chapter
        if current_chapter_lines:
            chapter_text = '\n'.join(current_chapter_lines).strip()
            if self._is_valid_chapter(chapter_text):
                chapters.append(ChapterData(
                    chapter_number=current_chapter_num if current_chapter_num > 0 else 1,
                    title=current_title,
                    text=chapter_text,
                    word_count=len(chapter_text.split())
                ))

        # If no chapters detected, treat entire text as one chapter
        if not chapters:
            chapters.append(ChapterData(
                chapter_number=1,
                title=None,
                text=text.strip(),
                word_count=len(text.split())
            ))

        return chapters

    def _parse_chapter_number(self, num_str: str) -> int:
        """Parse chapter number from string (handles roman numerals)."""
        # Try to parse as integer first
        try:
            return int(num_str)
        except ValueError:
            pass

        # Try roman numeral
        return self._roman_to_int(num_str.upper())

    def _roman_to_int(self, s: str) -> int:
        """Convert roman numeral to integer."""
        roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        total = 0
        prev_value = 0

        for char in reversed(s):
            value = roman.get(char, 0)
            if value < prev_value:
                total -= value
            else:
                total += value
            prev_value = value

        return total if total > 0 else 1

    def _is_valid_chapter(self, text: str) -> bool:
        """Check if chapter meets minimum requirements."""
        word_count = len(text.split())
        return word_count >= self.min_chapter_length

    def _extract_title(self, text: str) -> Optional[str]:
        """Try to extract book title from first few lines."""
        lines = text.split('\n')[:10]
        for line in lines:
            line = line.strip()
            if line and len(line) < 100 and len(line.split()) > 1:
                # Likely a title
                return line
        return None
