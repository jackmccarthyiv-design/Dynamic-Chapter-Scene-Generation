#!/usr/bin/env python3
"""Main CLI for Dynamic Chapter Scene Generation."""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

from src.pipeline import LandscapeGenerationPipeline
from rich.console import Console

# Load environment variables
load_dotenv()

console = Console()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate cinematic landscape videos from book chapters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a book and generate all videos
  python main.py --book examples/my_book.txt

  # Process first 3 chapters only (for testing)
  python main.py --book my_book.txt --max-chapters 3

  # Generate blueprints only (no rendering)
  python main.py --book my_book.txt --no-render

  # Specify output directory
  python main.py --book my_book.txt --output ./my_output

  # With custom book metadata
  python main.py --book book.txt --title "My Novel" --genre "fantasy"
        """
    )

    parser.add_argument(
        '--book',
        type=Path,
        required=True,
        help='Path to the book text file'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default='./output',
        help='Output directory (default: ./output)'
    )

    parser.add_argument(
        '--title',
        type=str,
        help='Book title (optional, will be extracted if not provided)'
    )

    parser.add_argument(
        '--genre',
        type=str,
        help='Book genre (optional, e.g., fantasy, sci-fi, literary)'
    )

    parser.add_argument(
        '--max-chapters',
        type=int,
        help='Maximum number of chapters to process (useful for testing)'
    )

    parser.add_argument(
        '--no-render',
        action='store_true',
        help='Skip video rendering, only generate blueprints'
    )

    parser.add_argument(
        '--config',
        type=Path,
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )

    parser.add_argument(
        '--show-stats',
        action='store_true',
        help='Show vector database statistics'
    )

    parser.add_argument(
        '--find-patterns',
        type=str,
        help='Find visual patterns for an emotion (e.g., "fear", "hope")'
    )

    args = parser.parse_args()

    # Validate book file exists
    if not args.book.exists():
        console.print(f"[red]Error:[/red] Book file not found: {args.book}")
        sys.exit(1)

    # Initialize pipeline
    pipeline = LandscapeGenerationPipeline(
        config_path=str(args.config) if args.config.exists() else None,
        output_base_dir=str(args.output)
    )

    # Handle special commands
    if args.show_stats:
        stats = pipeline.get_vector_store_stats()
        console.print("\n[bold cyan]Vector Database Statistics:[/bold cyan]")
        console.print(f"Total scenes stored: {stats['total_scenes']}")
        console.print(f"Collection: {stats['collection_name']}")
        return

    if args.find_patterns:
        console.print(f"\n[bold cyan]Finding patterns for:[/bold cyan] {args.find_patterns}")
        insights = pipeline.find_similar_patterns(emotion=args.find_patterns)
        console.print(f"\nExamples found: {insights['examples_found']}")

        if insights['common_weather']:
            console.print("\n[yellow]Common weather:[/yellow]")
            for weather, count in insights['common_weather']:
                console.print(f"  - {weather}: {count}")

        if insights['common_time_of_day']:
            console.print("\n[yellow]Common time of day:[/yellow]")
            for time, count in insights['common_time_of_day']:
                console.print(f"  - {time}: {count}")

        if insights['example_motifs']:
            console.print("\n[yellow]Common motifs:[/yellow]")
            for motif in insights['example_motifs'][:10]:
                console.print(f"  - {motif}")
        return

    # Process book
    try:
        results = pipeline.process_book(
            book_path=args.book,
            book_title=args.title,
            genre=args.genre,
            max_chapters=args.max_chapters,
            render_videos=not args.no_render
        )

        console.print("\n[bold green]✓ Processing complete![/bold green]")
        console.print(f"\nChapters processed: {results['chapters_processed']}")
        console.print(f"Output directory: {results['output_dir']}")

        if not args.no_render:
            successful_renders = sum(1 for r in results['render_results'] if r.get('success'))
            console.print(f"Videos rendered: {successful_renders}/{len(results['render_results'])}")

    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
