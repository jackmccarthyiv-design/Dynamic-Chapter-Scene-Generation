"""Vector database for cross-book learning and pattern recognition."""

import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from ..models import SceneBlueprint, ChapterData


class SceneVectorStore:
    """Store and retrieve scene patterns using vector embeddings."""

    def __init__(self, persist_dir: Optional[str] = None, collection_name: str = "chapter_scenes"):
        """
        Initialize vector store.

        Args:
            persist_dir: Directory to persist the database
            collection_name: Name of the collection to use
        """
        if persist_dir is None:
            persist_dir = os.getenv('CHROMA_PERSIST_DIR', './data/chroma_db')

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Scene blueprints from analyzed chapters"}
        )

        # Initialize embedding model
        model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
        self.embedding_model = SentenceTransformer(model_name)

    def add_scene(
        self,
        chapter: ChapterData,
        blueprint: SceneBlueprint,
        book_title: Optional[str] = None,
        genre: Optional[str] = None
    ):
        """
        Add a scene blueprint to the vector store.

        Args:
            chapter: Chapter data
            blueprint: Scene blueprint
            book_title: Title of the book
            genre: Genre of the book
        """
        # Create a text representation for embedding
        scene_text = self._blueprint_to_text(blueprint, chapter)

        # Generate embedding
        embedding = self.embedding_model.encode(scene_text).tolist()

        # Create metadata
        metadata = {
            "chapter_number": blueprint.chapter,
            "biome": blueprint.biome,
            "weather": blueprint.weather,
            "time_of_day": blueprint.time_of_day,
            "emotional_proxy": blueprint.emotional_proxy,
            "motifs": ",".join(blueprint.motifs),
            "book_title": book_title or "unknown",
            "genre": genre or "unknown",
        }

        # Create unique ID
        doc_id = f"{book_title or 'unknown'}_{blueprint.chapter}_{chapter.chapter_number}"

        # Add to collection
        self.collection.add(
            embeddings=[embedding],
            documents=[scene_text],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def find_similar_scenes(
        self,
        chapter: ChapterData,
        blueprint: Optional[SceneBlueprint] = None,
        n_results: int = 5,
        filter_by: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar scenes from previous books.

        Args:
            chapter: Chapter to find similar scenes for
            blueprint: Optional blueprint to use for similarity
            n_results: Number of results to return
            filter_by: Optional metadata filter

        Returns:
            List of similar scenes with metadata
        """
        # Create query text
        if blueprint:
            query_text = self._blueprint_to_text(blueprint, chapter)
        else:
            # Use chapter text directly
            query_text = chapter.text[:500]  # First 500 chars

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query_text).tolist()

        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_by
        )

        # Format results
        similar_scenes = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                similar_scenes.append({
                    'id': results['ids'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'metadata': results['metadatas'][0][i] if 'metadatas' in results else {},
                    'document': results['documents'][0][i] if 'documents' in results else ""
                })

        return similar_scenes

    def get_pattern_insights(
        self,
        emotional_proxy: str,
        biome: Optional[str] = None,
        n_results: int = 10
    ) -> Dict[str, Any]:
        """
        Get insights about visual patterns for a given emotion/biome.

        Args:
            emotional_proxy: Emotion to analyze (e.g., "fear", "hope")
            biome: Optional biome filter
            n_results: Number of examples to retrieve

        Returns:
            Pattern insights with common elements
        """
        # Build filter
        where_filter = {"emotional_proxy": {"$eq": emotional_proxy}}
        if biome:
            where_filter["biome"] = {"$eq": biome}

        # Query for examples
        results = self.collection.query(
            query_embeddings=[self.embedding_model.encode(emotional_proxy).tolist()],
            n_results=n_results,
            where=where_filter
        )

        # Analyze patterns
        insights = {
            "emotional_proxy": emotional_proxy,
            "biome_filter": biome,
            "examples_found": len(results['ids'][0]) if results['ids'] else 0,
            "common_weather": self._extract_common_values(results, 'weather'),
            "common_time_of_day": self._extract_common_values(results, 'time_of_day'),
            "common_biomes": self._extract_common_values(results, 'biome'),
            "example_motifs": self._extract_motifs(results)
        }

        return insights

    def _blueprint_to_text(self, blueprint: SceneBlueprint, chapter: ChapterData) -> str:
        """Convert blueprint to text for embedding."""
        parts = [
            f"Biome: {blueprint.biome}",
            f"Weather: {blueprint.weather}",
            f"Time: {blueprint.time_of_day}",
            f"Mood: {blueprint.emotional_proxy}",
            f"Motifs: {', '.join(blueprint.motifs)}",
            f"Lighting: {blueprint.lighting}",
            f"Colors: {', '.join(blueprint.palette)}",
        ]

        # Add some chapter context
        if blueprint.emotional_arc:
            parts.append(f"Arc: {blueprint.emotional_arc}")

        if blueprint.symbolic_elements:
            parts.append(f"Symbols: {', '.join(blueprint.symbolic_elements)}")

        # Add snippet of chapter text
        parts.append(f"Context: {chapter.text[:200]}")

        return " | ".join(parts)

    def _extract_common_values(self, results: Dict, field: str) -> List[tuple[str, int]]:
        """Extract most common values for a metadata field."""
        if not results['metadatas'] or not results['metadatas'][0]:
            return []

        values = {}
        for metadata in results['metadatas'][0]:
            value = metadata.get(field)
            if value:
                values[value] = values.get(value, 0) + 1

        # Sort by frequency
        return sorted(values.items(), key=lambda x: x[1], reverse=True)[:5]

    def _extract_motifs(self, results: Dict) -> List[str]:
        """Extract common motifs from results."""
        if not results['metadatas'] or not results['metadatas'][0]:
            return []

        all_motifs = []
        for metadata in results['metadatas'][0]:
            motifs_str = metadata.get('motifs', '')
            if motifs_str:
                all_motifs.extend(motifs_str.split(','))

        # Count and return top motifs
        motif_counts = {}
        for motif in all_motifs:
            motif = motif.strip()
            if motif:
                motif_counts[motif] = motif_counts.get(motif, 0) + 1

        return [m for m, c in sorted(motif_counts.items(), key=lambda x: x[1], reverse=True)[:10]]

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_scenes": self.collection.count(),
            "collection_name": self.collection.name,
        }
