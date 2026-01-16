"""Video rendering pipeline using Blender."""

import subprocess
import os
from pathlib import Path
from typing import Optional
import json

from ..models import SceneBlueprint


class VideoRenderer:
    """Render looping videos from Blender scenes."""

    def __init__(self, blender_path: Optional[str] = None):
        """
        Initialize renderer.

        Args:
            blender_path: Path to Blender executable
        """
        self.blender_path = blender_path or os.getenv('BLENDER_PATH', 'blender')

    def generate_scene_and_render(
        self,
        blueprint: SceneBlueprint,
        output_dir: Path,
        duration: int = 10,
        resolution: tuple[int, int] = (1920, 1080),
        fps: int = 30
    ) -> dict:
        """
        Generate Blender scene from blueprint and render video.

        Args:
            blueprint: Scene blueprint
            output_dir: Output directory
            duration: Video duration in seconds
            resolution: Video resolution (width, height)
            fps: Frames per second

        Returns:
            Dict with paths to generated files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save blueprint as JSON
        blueprint_path = output_dir / "blueprint.json"
        with open(blueprint_path, 'w') as f:
            # Convert blueprint to dict, handling nested models
            blueprint_dict = blueprint.model_dump()
            json.dump(blueprint_dict, f, indent=2)

        # Define output paths
        blend_file = output_dir / "scene.blend"
        video_file = output_dir / "landscape_loop.mp4"

        # Get path to Blender scene generator script
        script_path = Path(__file__).parent.parent / "generators" / "blender_scene.py"

        # Run Blender to generate scene
        print(f"Generating Blender scene for Chapter {blueprint.chapter}...")
        self._run_blender_script(
            script_path=script_path,
            args=[str(blueprint_path), str(blend_file)],
            background=True
        )

        # Render video
        print(f"Rendering video for Chapter {blueprint.chapter}...")
        self._render_video(
            blend_file=blend_file,
            output_path=video_file,
            duration=duration,
            resolution=resolution,
            fps=fps
        )

        return {
            "blueprint": str(blueprint_path),
            "blend_file": str(blend_file),
            "video": str(video_file),
            "success": video_file.exists()
        }

    def _run_blender_script(
        self,
        script_path: Path,
        args: list[str],
        background: bool = True
    ):
        """
        Run a Python script inside Blender.

        Args:
            script_path: Path to the Python script
            args: Arguments to pass to the script
            background: Run Blender in background mode
        """
        cmd = [self.blender_path]

        if background:
            cmd.extend(['--background'])

        cmd.extend([
            '--python', str(script_path),
            '--'
        ])
        cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("Warnings:", result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Blender script failed: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise

    def _render_video(
        self,
        blend_file: Path,
        output_path: Path,
        duration: int,
        resolution: tuple[int, int],
        fps: int
    ):
        """
        Render video from Blender file.

        Args:
            blend_file: Path to .blend file
            output_path: Output video path
            duration: Duration in seconds
            resolution: (width, height)
            fps: Frames per second
        """
        # Calculate frame range
        start_frame = 1
        end_frame = duration * fps

        # Build Blender command for rendering
        cmd = [
            self.blender_path,
            '--background',
            str(blend_file),
            '--render-output', str(output_path.parent / output_path.stem),
            '--render-format', 'FFMPEG',
            '--python-expr',
            f"import bpy; "
            f"bpy.context.scene.render.resolution_x = {resolution[0]}; "
            f"bpy.context.scene.render.resolution_y = {resolution[1]}; "
            f"bpy.context.scene.render.fps = {fps}; "
            f"bpy.context.scene.frame_start = {start_frame}; "
            f"bpy.context.scene.frame_end = {end_frame}; "
            f"bpy.context.scene.render.filepath = '{output_path}'; "
            f"bpy.context.scene.render.image_settings.file_format = 'FFMPEG'; "
            f"bpy.ops.render.render(animation=True, write_still=True)",
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            print("Render complete!")
            if result.stderr:
                print("Render warnings:", result.stderr)
        except subprocess.TimeoutExpired:
            print(f"Rendering timed out after 10 minutes")
            raise
        except subprocess.CalledProcessError as e:
            print(f"Rendering failed: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise

    def create_transition_video(
        self,
        from_scene: Path,
        to_scene: Path,
        output_path: Path,
        duration: float = 2.0
    ):
        """
        Create a transition video between two scenes.

        Args:
            from_scene: Path to first scene video
            to_scene: Path to second scene video
            output_path: Output transition video path
            duration: Transition duration in seconds
        """
        # Use ffmpeg to create cross-fade transition
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-i', str(from_scene),
            '-i', str(to_scene),
            '-filter_complex',
            f'[0:v][1:v]xfade=transition=fade:duration={duration}:offset=0[v]',
            '-map', '[v]',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Transition created: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Transition creation failed: {e}")
            print(f"stderr: {e.stderr}")
            raise
        except FileNotFoundError:
            print("ffmpeg not found. Please install ffmpeg for transition videos.")
            raise

    def concatenate_videos(
        self,
        video_paths: list[Path],
        output_path: Path,
        include_transitions: bool = True
    ):
        """
        Concatenate multiple videos into one.

        Args:
            video_paths: List of video file paths
            output_path: Output video path
            include_transitions: Whether to include cross-fade transitions
        """
        if not video_paths:
            return

        # Create concat file list
        concat_file = output_path.parent / "concat_list.txt"
        with open(concat_file, 'w') as f:
            for video_path in video_paths:
                f.write(f"file '{video_path.absolute()}'\n")

        # Concatenate using ffmpeg
        cmd = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Full film created: {output_path}")
            concat_file.unlink()  # Clean up
        except subprocess.CalledProcessError as e:
            print(f"Video concatenation failed: {e}")
            print(f"stderr: {e.stderr}")
            raise
