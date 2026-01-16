#!/usr/bin/env python3
"""
Full rendering pipeline test for the Way Station scene.
Validates all components and generates a visual preview using available tools.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Check for PIL/Pillow for image generation
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Note: PIL not available - will generate text-based visualization")

# Check for Blender
import shutil
BLENDER_PATH = shutil.which('blender')
HAS_BLENDER = BLENDER_PATH is not None


def create_scene_blueprint():
    """Create the Way Station scene blueprint."""
    return {
        "chapter": 1,
        "title": "The Way Station",
        "biome": "desert_basin",
        "weather": "dust",
        "time_of_day": "afternoon",
        "lighting": "harsh exterior light bleaching stone white, dim interior with dust motes in light shafts",
        "palette": [
            "#F5F0E6",  # bleached bone white
            "#D4C9B0",  # pale sand
            "#9A9590",  # dust gray
            "#8B7355",  # weathered wood brown
            "#C9A962",  # heat shimmer gold
            "#6B7B8C"   # shadow cool
        ],
        "camera": {
            "angle": "exterior establishing to threshold POV",
            "movement": "slow_dolly_forward"
        },
        "motifs": [
            "low stone building",
            "heavy wooden door",
            "narrow windows",
            "heat shimmer",
            "dust motes in light"
        ],
        "emotional_proxy": "survival without comfort, liminality as permanent state"
    }


def generate_blender_script(blueprint: dict, output_blend: str) -> str:
    """Generate the Blender Python script that would create the scene."""

    script = f'''#!/usr/bin/env python3
"""Auto-generated Blender scene script for: {blueprint['title']}"""

import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# === TERRAIN ===
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
terrain = bpy.context.active_object
terrain.name = "Desert_Terrain"

# Subdivide for displacement
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=50)
bpy.ops.object.mode_set(mode='OBJECT')

# Add displacement modifier for desert basin
displace = terrain.modifiers.new(name='TerrainDisplace', type='DISPLACE')
tex = bpy.data.textures.new('DesertNoise', type='CLOUDS')
tex.noise_scale = 8.0  # desert_basin setting
displace.texture = tex
displace.strength = 3.0  # gentle undulation

# Terrain material - pale sand color
mat_terrain = bpy.data.materials.new(name="DesertMaterial")
mat_terrain.use_nodes = True
nodes = mat_terrain.node_tree.nodes
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.83, 0.79, 0.69, 1.0)  # pale sand
bsdf.inputs['Roughness'].default_value = 0.95
output = nodes.new('ShaderNodeOutputMaterial')
mat_terrain.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
terrain.data.materials.append(mat_terrain)

# === WAY STATION BUILDING ===
# Main structure - low rectangular building
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 15, 1.5))
building = bpy.context.active_object
building.name = "WayStation"
building.scale = (4, 6, 3)  # low, wide structure

# Building material - bleached stone
mat_stone = bpy.data.materials.new(name="BleachedStone")
mat_stone.use_nodes = True
nodes = mat_stone.node_tree.nodes
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.96, 0.94, 0.90, 1.0)  # bleached white
bsdf.inputs['Roughness'].default_value = 0.85
output = nodes.new('ShaderNodeOutputMaterial')
mat_stone.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
building.data.materials.append(mat_stone)

# Door placeholder
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 12, 1))
door = bpy.context.active_object
door.name = "Door"
door.scale = (0.8, 0.1, 2)
mat_wood = bpy.data.materials.new(name="WeatheredWood")
mat_wood.use_nodes = True
nodes = mat_wood.node_tree.nodes
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.55, 0.45, 0.33, 1.0)  # wood brown
bsdf.inputs['Roughness'].default_value = 0.9
output = nodes.new('ShaderNodeOutputMaterial')
mat_wood.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
door.data.materials.append(mat_wood)

# === DISTANT HILLS ===
for i, x_offset in enumerate([-40, -20, 20, 40]):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=8, location=(x_offset, 60, -3))
    hill = bpy.context.active_object
    hill.name = f"DistantHill_{{i}}"
    hill.scale = (3, 2, 0.3)  # flattened, tired-looking
    hill.data.materials.append(mat_terrain)

# === CAMERA ===
cam_data = bpy.data.cameras.new('Camera')
cam_obj = bpy.data.objects.new('Camera', cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = (0, -25, 5)
cam_obj.rotation_euler = (math.radians(80), 0, 0)

# Camera animation - slow dolly forward
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 300  # 10 seconds at 30fps
cam_obj.keyframe_insert(data_path='location', frame=1)
cam_obj.location.y = -15  # move forward
cam_obj.keyframe_insert(data_path='location', frame=300)

# === LIGHTING - Afternoon Sun ===
light_data = bpy.data.lights.new('Sun', type='SUN')
light_data.energy = 4.0
light_data.color = (1.0, 0.95, 0.85)  # slightly warm
light_obj = bpy.data.objects.new('Sun', light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.rotation_euler = (math.radians(60), 0, math.radians(30))

# === WORLD/SKY ===
world = bpy.data.worlds.get('World') or bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
if bg:
    bg.inputs['Color'].default_value = (0.85, 0.88, 0.95, 1.0)  # pale washed sky
    bg.inputs['Strength'].default_value = 1.2

# === RENDER SETTINGS ===
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.fps = 30
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'

# Save scene
bpy.ops.wm.save_as_mainfile(filepath="{output_blend}")
print("Scene generated: {output_blend}")
'''
    return script


def create_visual_preview(blueprint: dict, output_path: Path):
    """Create a visual preview image of the scene."""

    if not HAS_PIL:
        return None

    # Create image
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Parse palette colors
    colors = []
    for hex_color in blueprint['palette']:
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        colors.append(rgb)

    # Sky gradient (pale washed out)
    sky_color = colors[0]  # bleached bone white
    for y in range(height // 2):
        factor = y / (height // 2)
        r = int(sky_color[0] * (1 - factor * 0.1))
        g = int(sky_color[1] * (1 - factor * 0.05))
        b = int(sky_color[2] + factor * 20)
        draw.line([(0, y), (width, y)], fill=(min(255, r), min(255, g), min(255, b)))

    # Ground (pale sand)
    ground_color = colors[1]  # pale sand
    horizon = height // 2
    for y in range(horizon, height):
        factor = (y - horizon) / (height - horizon)
        r = int(ground_color[0] * (1 - factor * 0.15))
        g = int(ground_color[1] * (1 - factor * 0.15))
        b = int(ground_color[2] * (1 - factor * 0.1))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Distant hills (dust gray, very faint)
    hill_color = colors[2]  # dust gray
    hill_y = horizon - 30
    for i, x_center in enumerate([300, 600, 1300, 1600]):
        hill_width = 400 + i * 50
        hill_height = 40 + i * 10
        for dy in range(hill_height):
            alpha = 1 - (dy / hill_height) * 0.7
            y = hill_y + dy
            x_left = x_center - int(hill_width * (1 - dy / hill_height) / 2)
            x_right = x_center + int(hill_width * (1 - dy / hill_height) / 2)
            r = int(hill_color[0] * alpha + sky_color[0] * (1 - alpha))
            g = int(hill_color[1] * alpha + sky_color[1] * (1 - alpha))
            b = int(hill_color[2] * alpha + sky_color[2] * (1 - alpha))
            draw.line([(x_left, y), (x_right, y)], fill=(r, g, b))

    # Way Station building
    building_color = colors[0]  # bleached stone
    shadow_color = colors[5]  # shadow cool
    wood_color = colors[3]  # weathered wood

    # Building body
    bx, by = width // 2 - 100, horizon + 50
    bw, bh = 200, 100

    # Shadow side
    draw.polygon([
        (bx + bw, by),
        (bx + bw + 20, by + 10),
        (bx + bw + 20, by + bh + 10),
        (bx + bw, by + bh)
    ], fill=shadow_color)

    # Main face
    draw.rectangle([bx, by, bx + bw, by + bh], fill=building_color)

    # Roof (barely visible)
    draw.polygon([
        (bx - 5, by),
        (bx + bw + 5, by),
        (bx + bw + 25, by - 10),
        (bx - 5, by - 10)
    ], fill=(colors[2][0] - 20, colors[2][1] - 20, colors[2][2] - 20))

    # Door
    door_x = bx + bw // 2 - 15
    door_y = by + bh - 60
    draw.rectangle([door_x, door_y, door_x + 30, by + bh], fill=wood_color)

    # Narrow windows
    window_color = (60, 60, 70)  # dark interior
    for wx in [bx + 30, bx + bw - 50]:
        draw.rectangle([wx, by + 20, wx + 15, by + 50], fill=window_color)

    # Heat shimmer effect (subtle horizontal distortion lines)
    shimmer_color = colors[4]  # heat shimmer gold
    for y in range(horizon - 50, horizon + 30, 8):
        for x in range(0, width, 100):
            alpha = 0.1
            draw.line([(x, y), (x + 50, y)], fill=(*shimmer_color, 30), width=1)

    # Add text overlay
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Title
    draw.text((50, 50), "THE WAY STATION", fill=(50, 50, 50), font=font_large)
    draw.text((50, 100), "Scene Render Preview", fill=(100, 100, 100), font=font_small)

    # Scene info
    info_y = 150
    draw.text((50, info_y), f"Biome: {blueprint['biome']}", fill=(80, 80, 80), font=font_small)
    draw.text((50, info_y + 25), f"Weather: {blueprint['weather']}", fill=(80, 80, 80), font=font_small)
    draw.text((50, info_y + 50), f"Time: {blueprint['time_of_day']}", fill=(80, 80, 80), font=font_small)
    draw.text((50, info_y + 75), f"Camera: {blueprint['camera']['movement']}", fill=(80, 80, 80), font=font_small)

    # Palette swatches
    swatch_y = height - 100
    draw.text((50, swatch_y - 30), "Color Palette:", fill=(80, 80, 80), font=font_small)
    for i, color in enumerate(colors):
        sx = 50 + i * 60
        draw.rectangle([sx, swatch_y, sx + 50, swatch_y + 50], fill=color, outline=(100, 100, 100))

    # Emotional proxy
    draw.text((50, height - 40), f'"{blueprint["emotional_proxy"]}"', fill=(100, 100, 100), font=font_small)

    # Save
    img.save(output_path)
    return output_path


def validate_blender_script(script: str) -> dict:
    """Validate the generated Blender script for syntax and completeness."""

    validation = {
        'syntax_valid': True,
        'has_terrain': False,
        'has_building': False,
        'has_camera': False,
        'has_lighting': False,
        'has_materials': False,
        'has_animation': False,
        'has_render_settings': False,
        'errors': []
    }

    # Check syntax
    try:
        compile(script, '<string>', 'exec')
    except SyntaxError as e:
        validation['syntax_valid'] = False
        validation['errors'].append(f"Syntax error: {e}")

    # Check components
    validation['has_terrain'] = 'primitive_plane_add' in script
    validation['has_building'] = 'WayStation' in script
    validation['has_camera'] = "cameras.new('Camera')" in script
    validation['has_lighting'] = "lights.new('Sun'" in script
    validation['has_materials'] = 'materials.new' in script
    validation['has_animation'] = 'keyframe_insert' in script
    validation['has_render_settings'] = 'render.engine' in script

    return validation


def main():
    print("=" * 70)
    print("WAY STATION - FULL RENDER PIPELINE TEST")
    print("=" * 70)
    print(f"Test Time: {datetime.now().isoformat()}")
    print(f"Blender Available: {HAS_BLENDER} ({BLENDER_PATH or 'Not found'})")
    print(f"PIL Available: {HAS_PIL}")

    # Create output directory
    output_dir = Path("output/way_station_render_test")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Phase 1: Create Blueprint
    print("\n" + "=" * 70)
    print("PHASE 1: SCENE BLUEPRINT")
    print("=" * 70)

    blueprint = create_scene_blueprint()
    blueprint_path = output_dir / "scene_blueprint.json"
    blueprint_path.write_text(json.dumps(blueprint, indent=2))
    print(f"Blueprint created: {blueprint_path}")
    print(f"  Biome: {blueprint['biome']}")
    print(f"  Weather: {blueprint['weather']}")
    print(f"  Time: {blueprint['time_of_day']}")
    print(f"  Motifs: {len(blueprint['motifs'])}")

    # Phase 2: Generate Blender Script
    print("\n" + "=" * 70)
    print("PHASE 2: BLENDER SCRIPT GENERATION")
    print("=" * 70)

    blend_file = output_dir / "way_station.blend"
    blender_script = generate_blender_script(blueprint, str(blend_file))
    script_path = output_dir / "generate_scene.py"
    script_path.write_text(blender_script)
    print(f"Blender script generated: {script_path}")
    print(f"  Lines of code: {len(blender_script.splitlines())}")

    # Phase 3: Validate Script
    print("\n" + "=" * 70)
    print("PHASE 3: SCRIPT VALIDATION")
    print("=" * 70)

    validation = validate_blender_script(blender_script)
    print(f"Syntax valid: {validation['syntax_valid']}")
    print(f"Has terrain: {validation['has_terrain']}")
    print(f"Has building: {validation['has_building']}")
    print(f"Has camera: {validation['has_camera']}")
    print(f"Has lighting: {validation['has_lighting']}")
    print(f"Has materials: {validation['has_materials']}")
    print(f"Has animation: {validation['has_animation']}")
    print(f"Has render settings: {validation['has_render_settings']}")

    if validation['errors']:
        print(f"Errors: {validation['errors']}")

    # Phase 4: Visual Preview
    print("\n" + "=" * 70)
    print("PHASE 4: VISUAL PREVIEW GENERATION")
    print("=" * 70)

    if HAS_PIL:
        preview_path = output_dir / "scene_preview.png"
        create_visual_preview(blueprint, preview_path)
        print(f"Preview image generated: {preview_path}")
    else:
        print("PIL not available - skipping visual preview")

    # Phase 5: Blender Execution (if available)
    print("\n" + "=" * 70)
    print("PHASE 5: BLENDER EXECUTION")
    print("=" * 70)

    if HAS_BLENDER:
        print(f"Executing Blender script...")
        import subprocess
        try:
            result = subprocess.run(
                [BLENDER_PATH, '--background', '--python', str(script_path)],
                capture_output=True,
                text=True,
                timeout=120
            )
            print(f"Blender exit code: {result.returncode}")
            if result.returncode == 0:
                print(f"Scene file created: {blend_file}")
                if blend_file.exists():
                    print(f"  Size: {blend_file.stat().st_size / 1024:.1f} KB")
            else:
                print(f"Blender stderr: {result.stderr[:500]}")
        except subprocess.TimeoutExpired:
            print("Blender execution timed out (120s)")
        except Exception as e:
            print(f"Blender execution failed: {e}")
    else:
        print("Blender not available - script ready for manual execution")
        print(f"\nTo render manually, run:")
        print(f"  blender --background --python {script_path}")

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    all_valid = all([
        validation['syntax_valid'],
        validation['has_terrain'],
        validation['has_building'],
        validation['has_camera'],
        validation['has_lighting'],
        validation['has_materials'],
        validation['has_animation'],
        validation['has_render_settings']
    ])

    print(f"""
Generated Files:
  - {blueprint_path}
  - {script_path}
  {'- ' + str(output_dir / 'scene_preview.png') if HAS_PIL else ''}

Pipeline Validation:
  [{'OK' if validation['syntax_valid'] else 'FAIL'}] Python syntax
  [{'OK' if validation['has_terrain'] else 'FAIL'}] Terrain generation
  [{'OK' if validation['has_building'] else 'FAIL'}] Building (Way Station)
  [{'OK' if validation['has_camera'] else 'FAIL'}] Camera setup
  [{'OK' if validation['has_lighting'] else 'FAIL'}] Lighting
  [{'OK' if validation['has_materials'] else 'FAIL'}] Materials
  [{'OK' if validation['has_animation'] else 'FAIL'}] Camera animation
  [{'OK' if validation['has_render_settings'] else 'FAIL'}] Render settings

Blender Status:
  [{'OK' if HAS_BLENDER else '--'}] Blender {'installed' if HAS_BLENDER else 'NOT INSTALLED'}
  {'[OK] Scene file generated' if HAS_BLENDER and blend_file.exists() else '[--] Scene file (requires Blender)'}

Overall: {'READY FOR RENDERING' if all_valid else 'VALIDATION FAILED'}
""")

    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)

    return {
        'blueprint': blueprint,
        'script_path': str(script_path),
        'validation': validation,
        'blender_available': HAS_BLENDER
    }


if __name__ == "__main__":
    main()
