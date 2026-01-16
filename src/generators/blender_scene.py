"""Procedural scene generation script for Blender.

This script is designed to be executed inside Blender's Python environment.
It generates procedural 3D landscapes based on scene blueprints.
"""

import json
import sys
import math
import random
from pathlib import Path

# Check if running in Blender
try:
    import bpy
    import bmesh
    from mathutils import Vector, Color
except ImportError:
    print("Warning: bpy not available. This script must be run inside Blender.")
    bpy = None


class BlenderSceneGenerator:
    """Generate procedural 3D scenes in Blender."""

    def __init__(self):
        """Initialize the scene generator."""
        if bpy is None:
            raise RuntimeError("This script must be run inside Blender")

        self.scene = bpy.context.scene
        self.world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')

    def generate_from_blueprint(self, blueprint: dict, output_path: str):
        """
        Generate a complete scene from a blueprint.

        Args:
            blueprint: Scene blueprint dictionary
            output_path: Path to save the .blend file
        """
        # Clear existing scene
        self._clear_scene()

        # Set up world/environment
        self._setup_world(blueprint)

        # Generate terrain based on biome
        self._generate_terrain(blueprint)

        # Add atmospheric effects (fog, volumetrics)
        self._setup_atmosphere(blueprint)

        # Place motif objects
        self._place_motifs(blueprint)

        # Set up camera
        self._setup_camera(blueprint)

        # Set up lighting
        self._setup_lighting(blueprint)

        # Configure render settings
        self._setup_render_settings()

        # Save the blend file
        bpy.ops.wm.save_as_mainfile(filepath=output_path)
        print(f"Scene saved to: {output_path}")

    def _clear_scene(self):
        """Remove all objects from the scene."""
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

        # Clear orphaned data
        for block in bpy.data.meshes:
            if block.users == 0:
                bpy.data.meshes.remove(block)

    def _setup_world(self, blueprint: dict):
        """Set up world environment (sky, background)."""
        self.scene.world = self.world

        # Enable nodes
        self.world.use_nodes = True
        nodes = self.world.node_tree.nodes
        links = self.world.node_tree.links

        # Clear existing nodes
        nodes.clear()

        # Create sky texture based on time of day
        bg_node = nodes.new(type='ShaderNodeBackground')
        output_node = nodes.new(type='ShaderNodeOutputWorld')

        time_of_day = blueprint.get('time_of_day', 'noon')
        sky_color = self._get_sky_color(time_of_day, blueprint.get('weather', 'clear'))

        bg_node.inputs['Color'].default_value = sky_color
        bg_node.inputs['Strength'].default_value = self._get_sky_strength(time_of_day)

        links.new(bg_node.outputs['Background'], output_node.inputs['Surface'])

    def _generate_terrain(self, blueprint: dict):
        """Generate terrain mesh based on biome."""
        biome = blueprint.get('biome', 'grassland')

        # Create base plane
        bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
        terrain = bpy.context.active_object
        terrain.name = "Terrain"

        # Subdivide for detail
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=50)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Apply displacement based on biome
        self._apply_terrain_displacement(terrain, biome)

        # Add material
        self._add_terrain_material(terrain, blueprint)

        return terrain

    def _apply_terrain_displacement(self, terrain_obj, biome: str):
        """Apply procedural displacement to terrain."""
        # Add displacement modifier
        displace_mod = terrain_obj.modifiers.new(name='Displace', type='DISPLACE')

        # Create noise texture
        texture = bpy.data.textures.new(name='TerrainNoise', type='CLOUDS')

        # Configure based on biome
        biome_configs = {
            'alpine_meadow': {'scale': 5.0, 'strength': 8.0},
            'coastal_cliff': {'scale': 3.0, 'strength': 15.0},
            'desert_basin': {'scale': 8.0, 'strength': 3.0},
            'pine_forest': {'scale': 4.0, 'strength': 5.0},
            'canyon': {'scale': 2.0, 'strength': 20.0},
            'default': {'scale': 5.0, 'strength': 5.0}
        }

        config = biome_configs.get(biome, biome_configs['default'])
        texture.noise_scale = config['scale']
        displace_mod.texture = texture
        displace_mod.strength = config['strength']

    def _add_terrain_material(self, terrain_obj, blueprint: dict):
        """Add material to terrain based on palette."""
        mat = bpy.data.materials.new(name="TerrainMaterial")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        nodes.clear()

        # Base color from palette
        palette = blueprint.get('palette', ['#8B7355', '#A0A0A0'])
        base_color = self._hex_to_rgb(palette[0])

        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = base_color + (1.0,)
        bsdf.inputs['Roughness'].default_value = 0.9

        output = nodes.new(type='ShaderNodeOutputMaterial')
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

        terrain_obj.data.materials.append(mat)

    def _setup_atmosphere(self, blueprint: dict):
        """Set up atmospheric effects (fog, mist, volumetrics)."""
        weather = blueprint.get('weather', 'clear')

        if weather in ['fog', 'mist']:
            # Add volumetric fog
            self.world.use_nodes = True
            nodes = self.world.node_tree.nodes

            # Add volume scatter
            volume_scatter = nodes.new(type='ShaderNodeVolumeScatter')
            volume_scatter.inputs['Density'].default_value = 0.05

            # Connect to world output
            output = nodes.get('World Output')
            if output:
                self.world.node_tree.links.new(
                    volume_scatter.outputs['Volume'],
                    output.inputs['Volume']
                )

    def _place_motifs(self, blueprint: dict):
        """Place motif objects in the scene."""
        motifs = blueprint.get('motifs', [])

        for i, motif in enumerate(motifs[:5]):  # Limit to 5 motifs
            self._create_motif_object(motif, i)

    def _create_motif_object(self, motif: str, index: int):
        """Create a simple geometric representation of a motif."""
        # Map motifs to simple geometric shapes
        motif_lower = motif.lower()

        if any(word in motif_lower for word in ['tower', 'lighthouse', 'obelisk']):
            bpy.ops.mesh.primitive_cylinder_add(
                radius=1,
                depth=10,
                location=(index * 10 - 20, 20, 5)
            )
        elif any(word in motif_lower for word in ['rock', 'boulder', 'stone']):
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2,
                radius=2,
                location=(index * 10 - 20, 15, 1)
            )
        elif any(word in motif_lower for word in ['tree', 'pine']):
            bpy.ops.mesh.primitive_cone_add(
                radius1=2,
                depth=8,
                location=(index * 10 - 20, 10, 4)
            )

    def _setup_camera(self, blueprint: dict):
        """Set up camera with specified angle and movement."""
        camera_data = bpy.data.cameras.new(name='Camera')
        camera_obj = bpy.data.objects.new('Camera', camera_data)
        self.scene.collection.objects.link(camera_obj)
        self.scene.camera = camera_obj

        # Position camera based on angle
        camera_config = blueprint.get('camera', {})
        angle_desc = camera_config.get('angle', 'wide shot')

        if 'low' in angle_desc.lower():
            camera_obj.location = (0, -30, 2)
            camera_obj.rotation_euler = (math.radians(85), 0, 0)
        elif 'high' in angle_desc.lower():
            camera_obj.location = (0, -30, 20)
            camera_obj.rotation_euler = (math.radians(60), 0, 0)
        else:  # medium/wide
            camera_obj.location = (0, -35, 10)
            camera_obj.rotation_euler = (math.radians(75), 0, 0)

        # Set up camera animation for movement
        self._animate_camera(camera_obj, camera_config.get('movement', 'static'))

    def _animate_camera(self, camera_obj, movement: str):
        """Animate camera for looping movement."""
        fps = 30
        duration = 10  # seconds
        total_frames = fps * duration

        self.scene.frame_start = 1
        self.scene.frame_end = total_frames

        if movement == 'static':
            return

        # Set keyframes for seamless loop
        camera_obj.keyframe_insert(data_path='location', frame=1)
        camera_obj.keyframe_insert(data_path='rotation_euler', frame=1)

        if 'pan_left' in movement:
            camera_obj.rotation_euler.z += math.radians(15)
        elif 'pan_right' in movement:
            camera_obj.rotation_euler.z -= math.radians(15)
        elif 'dolly_forward' in movement:
            camera_obj.location.y += 10
        elif 'tilt_up' in movement:
            camera_obj.rotation_euler.x -= math.radians(10)

        camera_obj.keyframe_insert(data_path='location', frame=total_frames // 2)
        camera_obj.keyframe_insert(data_path='rotation_euler', frame=total_frames // 2)

        # Return to start for loop
        camera_obj.location = camera_obj.location
        camera_obj.rotation_euler = camera_obj.rotation_euler
        camera_obj.keyframe_insert(data_path='location', frame=total_frames)
        camera_obj.keyframe_insert(data_path='rotation_euler', frame=total_frames)

    def _setup_lighting(self, blueprint: dict):
        """Set up scene lighting based on time of day."""
        time_of_day = blueprint.get('time_of_day', 'noon')

        # Add sun light
        light_data = bpy.data.lights.new(name='Sun', type='SUN')
        light_obj = bpy.data.objects.new('Sun', light_data)
        self.scene.collection.objects.link(light_obj)

        # Configure sun based on time of day
        sun_configs = {
            'dawn': {'strength': 1.5, 'rotation': (math.radians(10), 0, 0), 'color': (1.0, 0.9, 0.7)},
            'noon': {'strength': 3.0, 'rotation': (math.radians(45), 0, 0), 'color': (1.0, 1.0, 1.0)},
            'dusk': {'strength': 1.0, 'rotation': (math.radians(5), 0, 0), 'color': (1.0, 0.6, 0.4)},
            'night': {'strength': 0.3, 'rotation': (math.radians(-10), 0, 0), 'color': (0.5, 0.5, 0.8)},
        }

        config = sun_configs.get(time_of_day, sun_configs['noon'])
        light_data.energy = config['strength']
        light_obj.rotation_euler = config['rotation']
        light_data.color = config['color']

    def _setup_render_settings(self):
        """Configure render settings for output."""
        self.scene.render.engine = 'CYCLES'
        self.scene.cycles.samples = 128
        self.scene.render.resolution_x = 1920
        self.scene.render.resolution_y = 1080
        self.scene.render.fps = 30

        # Enable denoising
        self.scene.cycles.use_denoising = True

        # Set output format
        self.scene.render.image_settings.file_format = 'FFMPEG'
        self.scene.render.ffmpeg.format = 'MPEG4'
        self.scene.render.ffmpeg.codec = 'H264'

    def _get_sky_color(self, time_of_day: str, weather: str) -> tuple:
        """Get sky color based on time and weather."""
        colors = {
            'dawn': (0.8, 0.6, 0.5, 1.0),
            'morning': (0.6, 0.7, 0.9, 1.0),
            'noon': (0.5, 0.7, 1.0, 1.0),
            'dusk': (0.9, 0.5, 0.4, 1.0),
            'night': (0.05, 0.05, 0.15, 1.0),
        }

        base_color = colors.get(time_of_day, colors['noon'])

        # Modify for weather
        if weather in ['fog', 'mist', 'overcast']:
            return tuple(c * 0.7 for c in base_color[:3]) + (1.0,)

        return base_color

    def _get_sky_strength(self, time_of_day: str) -> float:
        """Get sky emission strength."""
        strengths = {
            'dawn': 0.8,
            'morning': 1.0,
            'noon': 1.2,
            'dusk': 0.6,
            'night': 0.3,
        }
        return strengths.get(time_of_day, 1.0)

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        return (0.5, 0.5, 0.5)


def main():
    """Main entry point when running as Blender script."""
    if len(sys.argv) < 2:
        print("Usage: blender --background --python blender_scene.py -- <blueprint.json> <output.blend>")
        sys.exit(1)

    # Get arguments after --
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]

    blueprint_path = argv[0]
    output_path = argv[1] if len(argv) > 1 else "output.blend"

    # Load blueprint
    with open(blueprint_path, 'r') as f:
        blueprint = json.load(f)

    # Generate scene
    generator = BlenderSceneGenerator()
    generator.generate_from_blueprint(blueprint, output_path)

    print("Scene generation complete!")


if __name__ == "__main__":
    if bpy is not None:
        main()
