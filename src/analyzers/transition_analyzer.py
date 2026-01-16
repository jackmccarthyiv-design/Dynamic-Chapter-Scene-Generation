"""Analyze transitions between chapters."""

from typing import Optional
from ..models import SceneBlueprint, TransitionConfig


class TransitionAnalyzer:
    """Analyze how scenes should transition between chapters."""

    TRANSITION_TYPES = {
        'escalation': {
            'description': 'Tension increases, danger approaches',
            'visual_cues': ['sharper contrast', 'tighter framing', 'chaotic weather', 'darkening']
        },
        'revelation': {
            'description': 'Truth revealed, understanding gained',
            'visual_cues': ['expanding horizon', 'clearing skies', 'warmer tones', 'increased light']
        },
        'descent': {
            'description': 'Loss, decline, deterioration',
            'visual_cues': ['flattening light', 'heavier shadows', 'decay patterns', 'desaturation']
        },
        'journey': {
            'description': 'Physical or metaphorical movement',
            'visual_cues': ['changing terrain', 'path appearance', 'distance covered']
        },
        'stasis': {
            'description': 'Minimal change, waiting, contemplation',
            'visual_cues': ['subtle lighting shifts', 'same location', 'time passage']
        }
    }

    def analyze_transition(
        self,
        from_blueprint: SceneBlueprint,
        to_blueprint: SceneBlueprint
    ) -> TransitionConfig:
        """
        Analyze the transition between two scene blueprints.

        Args:
            from_blueprint: Previous chapter's scene
            to_blueprint: Next chapter's scene

        Returns:
            TransitionConfig describing the transition
        """
        # Determine transition type
        transition_type = self._determine_transition_type(from_blueprint, to_blueprint)

        # Find shared anchors (continuity elements)
        shared_anchors = self._find_shared_anchors(from_blueprint, to_blueprint)

        # Determine what elements morph
        morph_elements = self._analyze_morphing_elements(from_blueprint, to_blueprint)

        return TransitionConfig(
            from_chapter=from_blueprint.chapter,
            to_chapter=to_blueprint.chapter,
            transition_type=transition_type,
            duration=2.0,
            shared_anchors=shared_anchors,
            morph_elements=morph_elements
        )

    def _determine_transition_type(
        self,
        from_blueprint: SceneBlueprint,
        to_blueprint: SceneBlueprint
    ) -> str:
        """Determine the type of transition based on scene changes."""
        # Analyze emotional proxy changes
        from_emotion = from_blueprint.emotional_proxy.lower()
        to_emotion = to_blueprint.emotional_proxy.lower()

        # Simple heuristics for transition type
        tension_words = ['fear', 'tension', 'danger', 'threat', 'anxiety']
        positive_words = ['hope', 'joy', 'relief', 'peace', 'triumph']
        negative_words = ['loss', 'grief', 'defeat', 'despair', 'decline']

        from_has_tension = any(word in from_emotion for word in tension_words)
        to_has_tension = any(word in to_emotion for word in tension_words)

        from_positive = any(word in from_emotion for word in positive_words)
        to_positive = any(word in to_emotion for word in positive_words)

        to_negative = any(word in to_emotion for word in negative_words)

        if not from_has_tension and to_has_tension:
            return 'escalation'
        elif from_has_tension and to_positive:
            return 'revelation'
        elif to_negative or (from_positive and not to_positive):
            return 'descent'
        elif from_blueprint.biome != to_blueprint.biome:
            return 'journey'
        else:
            return 'stasis'

    def _find_shared_anchors(
        self,
        from_blueprint: SceneBlueprint,
        to_blueprint: SceneBlueprint
    ) -> list[str]:
        """Find visual elements that should persist across transition."""
        shared = []

        # Check if any continuity anchors match
        from_anchors = set(from_blueprint.continuity_anchors)
        to_anchors = set(to_blueprint.continuity_anchors)

        shared.extend(from_anchors.intersection(to_anchors))

        # Check for matching motifs
        from_motifs = set(from_blueprint.motifs)
        to_motifs = set(to_blueprint.motifs)

        shared.extend(from_motifs.intersection(to_motifs))

        return list(set(shared))  # Remove duplicates

    def _analyze_morphing_elements(
        self,
        from_blueprint: SceneBlueprint,
        to_blueprint: SceneBlueprint
    ) -> dict:
        """Analyze which elements change and how."""
        changes = {}

        if from_blueprint.biome != to_blueprint.biome:
            changes['biome'] = {
                'from': from_blueprint.biome,
                'to': to_blueprint.biome,
                'type': 'morph'
            }

        if from_blueprint.weather != to_blueprint.weather:
            changes['weather'] = {
                'from': from_blueprint.weather,
                'to': to_blueprint.weather,
                'type': 'transition'
            }

        if from_blueprint.time_of_day != to_blueprint.time_of_day:
            changes['time_of_day'] = {
                'from': from_blueprint.time_of_day,
                'to': to_blueprint.time_of_day,
                'type': 'time_shift'
            }

        if from_blueprint.lighting != to_blueprint.lighting:
            changes['lighting'] = {
                'from': from_blueprint.lighting,
                'to': to_blueprint.lighting,
                'type': 'fade'
            }

        # Analyze palette shift
        changes['palette'] = {
            'from': from_blueprint.palette,
            'to': to_blueprint.palette,
            'type': 'color_shift'
        }

        return changes

    def generate_transition_description(self, transition: TransitionConfig) -> str:
        """Generate a human-readable description of the transition."""
        desc_parts = [
            f"Transition from Chapter {transition.from_chapter} to {transition.to_chapter}",
            f"Type: {transition.transition_type}",
            f"Duration: {transition.duration}s"
        ]

        if transition.shared_anchors:
            desc_parts.append(f"Anchors: {', '.join(transition.shared_anchors)}")

        if transition.morph_elements:
            changes = []
            for element, change_data in transition.morph_elements.items():
                if element != 'palette':
                    changes.append(f"{element}: {change_data.get('from')} → {change_data.get('to')}")
            if changes:
                desc_parts.append("Changes: " + "; ".join(changes))

        return "\n".join(desc_parts)
