"""Main orchestration pipeline for book-to-landscape processing."""

import json
import time
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from .models import ChapterData, BookMetadata, SceneBlueprint, SceneGenerationResult
from .parsers import BookParser
from .analyzers import ChapterAnalyzer
from .analyzers.transition_analyzer import TransitionAnalyzer
from .database import SceneVectorStore
from .renderers import VideoRenderer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn


class LandscapeGenerationPipeline:
    """Complete pipeline for generating landscape films from books."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        output_base_dir: Optional[str] = None
    ):
        """
        Initialize pipeline.

        Args:
            config_path: Path to config.yaml
            output_base_dir: Base directory for all outputs
        """
        self.config_path = config_path or "config.yaml"
        self.output_base_dir = Path(output_base_dir or "./output")

        # Initialize components
        self.parser = BookParser()
        self.analyzer = ChapterAnalyzer(config_path=self.config_path)
        self.transition_analyzer = TransitionAnalyzer()
        self.vector_store = SceneVectorStore()
        self.renderer = VideoRenderer()

        # Console for rich output
        self.console = Console()

    def process_book(
        self,
        book_path: Path,
        book_title: Optional[str] = None,
        genre: Optional[str] = None,
        max_chapters: Optional[int] = None,
        render_videos: bool = True
    ) -> dict:
        """
        Process a complete book into landscape scenes.

        Args:
            book_path: Path to the book text file
            book_title: Optional book title (otherwise extracted)
            genre: Optional genre classification
            max_chapters: Optional limit on number of chapters to process
            render_videos: Whether to render videos (vs just generate blueprints)

        Returns:
            Dict with processing results
        """
        start_time = time.time()

        self.console.print(f"\n[bold cyan]Processing book:[/bold cyan] {book_path.name}")

        # 1. Parse book into chapters
        self.console.print("[yellow]Step 1:[/yellow] Parsing chapters...")
        chapters, metadata = self.parser.parse_file(book_path)

        if book_title:
            metadata.title = book_title
        if genre:
            metadata.genre = genre

        self.console.print(f"Found {len(chapters)} chapters, {metadata.total_words:,} words")

        if max_chapters:
            chapters = chapters[:max_chapters]
            self.console.print(f"Processing first {max_chapters} chapters")

        # Create output directory
        book_output_dir = self._create_output_directory(metadata)

        # Save metadata
        metadata_path = book_output_dir / "book_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata.model_dump(), f, indent=2)

        # 2. Analyze book context
        self.console.print("[yellow]Step 2:[/yellow] Analyzing book context...")
        book_context = self.analyzer.analyze_book_context(chapters)
        self.console.print(f"Context: {book_context}")

        # 3. Generate scene blueprints for each chapter
        self.console.print("[yellow]Step 3:[/yellow] Generating scene blueprints...")
        blueprints = self._generate_blueprints(chapters, book_context)

        # Save all blueprints
        blueprints_path = book_output_dir / "all_blueprints.json"
        with open(blueprints_path, 'w') as f:
            json.dump([bp.model_dump() for bp in blueprints], f, indent=2)

        # 4. Store in vector database for learning
        self.console.print("[yellow]Step 4:[/yellow] Storing patterns in vector database...")
        for chapter, blueprint in zip(chapters, blueprints):
            self.vector_store.add_scene(
                chapter=chapter,
                blueprint=blueprint,
                book_title=metadata.title,
                genre=metadata.genre
            )

        # 5. Analyze transitions
        self.console.print("[yellow]Step 5:[/yellow] Analyzing transitions...")
        transitions = self._analyze_transitions(blueprints)

        # Save transitions
        transitions_path = book_output_dir / "transitions.json"
        with open(transitions_path, 'w') as f:
            json.dump([t.model_dump() for t in transitions], f, indent=2)

        # 6. Render videos (if enabled)
        results = []
        video_paths = []

        if render_videos:
            self.console.print("[yellow]Step 6:[/yellow] Rendering landscape videos...")
            results = self._render_all_chapters(blueprints, book_output_dir)

            # Collect successful video paths
            video_paths = [
                Path(r['video']) for r in results
                if r['success'] and r.get('video')
            ]

            # 7. Create full film
            if video_paths:
                self.console.print("[yellow]Step 7:[/yellow] Creating full film...")
                full_film_path = book_output_dir / "full_film.mp4"
                try:
                    self.renderer.concatenate_videos(video_paths, full_film_path)
                    self.console.print(f"[green]Full film created:[/green] {full_film_path}")
                except Exception as e:
                    self.console.print(f"[red]Failed to create full film:[/red] {e}")

        # Summary
        elapsed = time.time() - start_time
        self.console.print(f"\n[bold green]Processing complete![/bold green]")
        self.console.print(f"Time elapsed: {elapsed:.1f}s")
        self.console.print(f"Output directory: {book_output_dir}")

        return {
            'book_title': metadata.title,
            'chapters_processed': len(chapters),
            'blueprints': blueprints,
            'transitions': transitions,
            'render_results': results,
            'output_dir': str(book_output_dir),
            'elapsed_time': elapsed
        }

    def _create_output_directory(self, metadata: BookMetadata) -> Path:
        """Create output directory for book."""
        # Use timestamp to ensure uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        book_slug = (metadata.title or "book").lower().replace(" ", "_")
        dir_name = f"{book_slug}_{timestamp}"

        output_dir = self.output_base_dir / dir_name
        output_dir.mkdir(parents=True, exist_ok=True)

        return output_dir

    def _generate_blueprints(
        self,
        chapters: List[ChapterData],
        book_context: str
    ) -> List[SceneBlueprint]:
        """Generate scene blueprints for all chapters."""
        blueprints = []
        previous_blueprint = None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("Analyzing chapters...", total=len(chapters))

            for chapter in chapters:
                try:
                    blueprint = self.analyzer.analyze_chapter(
                        chapter=chapter,
                        previous_blueprint=previous_blueprint,
                        book_context=book_context
                    )
                    blueprints.append(blueprint)
                    previous_blueprint = blueprint

                    progress.update(task, advance=1)
                except Exception as e:
                    self.console.print(f"[red]Error analyzing chapter {chapter.chapter_number}:[/red] {e}")
                    # Create a default blueprint
                    blueprints.append(self._create_default_blueprint(chapter))

        return blueprints

    def _analyze_transitions(
        self,
        blueprints: List[SceneBlueprint]
    ) -> List:
        """Analyze transitions between chapters."""
        transitions = []

        for i in range(len(blueprints) - 1):
            transition = self.transition_analyzer.analyze_transition(
                blueprints[i],
                blueprints[i + 1]
            )
            transitions.append(transition)

        return transitions

    def _render_all_chapters(
        self,
        blueprints: List[SceneBlueprint],
        output_dir: Path
    ) -> List[dict]:
        """Render videos for all chapters."""
        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            task = progress.add_task("Rendering videos...", total=len(blueprints))

            for blueprint in blueprints:
                chapter_dir = output_dir / f"chapter_{blueprint.chapter:02d}"

                try:
                    result = self.renderer.generate_scene_and_render(
                        blueprint=blueprint,
                        output_dir=chapter_dir
                    )
                    results.append(result)
                except Exception as e:
                    self.console.print(f"[red]Error rendering chapter {blueprint.chapter}:[/red] {e}")
                    results.append({
                        'chapter': blueprint.chapter,
                        'success': False,
                        'error': str(e)
                    })

                progress.update(task, advance=1)

        return results

    def _create_default_blueprint(self, chapter: ChapterData) -> SceneBlueprint:
        """Create a default blueprint when analysis fails."""
        from .models import CameraConfig

        return SceneBlueprint(
            chapter=chapter.chapter_number,
            title=chapter.title,
            biome="grassland",
            weather="clear",
            time_of_day="noon",
            lighting="natural daylight",
            palette=["#87CEEB", "#228B22", "#D2B48C"],
            camera=CameraConfig(angle="wide shot", movement="static"),
            motifs=["grass", "sky", "horizon"],
            emotional_proxy="neutral",
        )

    def get_vector_store_stats(self) -> dict:
        """Get statistics from the vector database."""
        return self.vector_store.get_stats()

    def find_similar_patterns(
        self,
        emotion: str,
        biome: Optional[str] = None
    ) -> dict:
        """Find similar visual patterns for an emotion/biome combination."""
        return self.vector_store.get_pattern_insights(
            emotional_proxy=emotion,
            biome=biome
        )
