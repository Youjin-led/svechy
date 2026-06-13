import json
import math
import random
from datetime import datetime
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
random.seed(202605263)


def input_socket(bsdf, names):
    for name in names:
        socket = bsdf.inputs.get(name)
        if socket:
            return socket
    return None


def set_socket(bsdf, names, value):
    socket = input_socket(bsdf, names)
    if socket:
        socket.default_value = value


def make_material(name, color, alpha, emission=None, emission_strength=0.0, roughness=0.32):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    mat.use_screen_refraction = True
    mat.show_transparent_back = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        set_socket(bsdf, ("Base Color",), color)
        set_socket(bsdf, ("Alpha",), alpha)
        set_socket(bsdf, ("Roughness",), roughness)
        set_socket(bsdf, ("Metallic",), 0.0)
        if emission:
            set_socket(bsdf, ("Emission Color", "Emission"), emission)
            set_socket(bsdf, ("Emission Strength",), emission_strength)
    return mat


BELL_MATS = [
    make_material("jellyfish_bell_pearl_cyan", (0.72, 0.96, 1.0, 0.42), 0.42, (0.18, 0.52, 0.72, 1), 0.18),
    make_material("jellyfish_bell_lilac_glass", (0.86, 0.72, 1.0, 0.40), 0.40, (0.45, 0.22, 0.82, 1), 0.22),
    make_material("jellyfish_bell_rose_glass", (1.0, 0.62, 0.78, 0.40), 0.40, (0.85, 0.22, 0.48, 1), 0.20),
]
RIM_MAT = make_material("jellyfish_orange_ruffle_glow", (1.0, 0.42, 0.20, 0.72), 0.72, (1.0, 0.22, 0.10, 1), 0.85)
ARM_MAT = make_material("jellyfish_peach_oral_arms", (1.0, 0.48, 0.36, 0.70), 0.70, (1.0, 0.18, 0.16, 1), 0.45)
TENTACLE_MAT = make_material("jellyfish_fine_pink_tentacles", (1.0, 0.50, 0.74, 0.58), 0.58, (0.82, 0.18, 0.45, 1), 0.52)
CORE_MAT = make_material("jellyfish_warm_inner_core", (1.0, 0.70, 0.48, 0.54), 0.54, (1.0, 0.34, 0.18, 1), 0.62)
HIDDEN_MAT = make_material("jellyfish_hidden_card_anchor", (0.0, 0.0, 0.0, 0.0), 0.0)


def create_bell_mesh(name, segments=64, rings=12):
    verts = []
    faces = []
    for r in range(rings + 1):
        t = r / rings
        dome = math.sin(t * math.pi * 0.5)
        y = 0.18 + math.cos(t * math.pi * 0.5) * 0.80
        for s in range(segments):
            a = (s / segments) * math.pi * 2.0
            rim_wave = 1.0 + math.sin(a * 12.0) * 0.045 * t
            x = math.cos(a) * dome * 1.05 * rim_wave
            depth_y = math.sin(a) * dome * 0.34 * rim_wave
            # Subtle scallops and panel-like vertical veins like the reference.
            y_panel = y - max(0.0, t - 0.70) * 0.10 * (0.5 + 0.5 * math.sin(a * 16.0))
            verts.append((x, depth_y, y_panel))
    top_center = len(verts)
    verts.append((0.0, 0.0, 1.02))
    for s in range(segments):
        faces.append((top_center, s, (s + 1) % segments))
    for r in range(rings):
        base = r * segments
        next_base = (r + 1) * segments
        for s in range(segments):
            faces.append((base + s, base + (s + 1) % segments, next_base + (s + 1) % segments, next_base + s))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def create_ribbon_mesh(name, length=1.80, width=0.18, segments=22, phase=0.0):
    verts = []
    faces = []
    for i in range(segments + 1):
        t = i / segments
        center_x = math.sin(t * 6.2 + phase) * 0.13 * (1.0 + t)
        center_z = -t * length
        center_depth = math.cos(t * 4.7 + phase * 0.8) * 0.07
        side_x = math.cos(t * 10.0 + phase) * width * (1.0 - t * 0.45)
        side_depth = math.sin(t * 8.0 + phase) * width * 0.24
        verts.append((center_x - side_x, center_depth - side_depth, center_z))
        verts.append((center_x + side_x, center_depth + side_depth, center_z))
    for i in range(segments):
        faces.append((i * 2, i * 2 + 1, i * 2 + 3, i * 2 + 2))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    return mesh


def make_curve_tentacle(name, points, bevel, material):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 3
    curve.bevel_depth = bevel
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, co in zip(spline.bezier_points, points):
        point.co = co
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    obj.data.materials.append(material)
    return obj


def add_child(parent, child, location=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)):
    bpy.context.collection.objects.link(child)
    child.parent = parent
    child.location = location
    child.rotation_euler = rotation
    child.scale = scale
    child.hide_viewport = False
    child.hide_render = False
    return child


def replace_card_with_jellyfish(card, index):
    old_mesh = card.data
    card.data = create_bell_mesh(f"jellyfish_card_bell_mesh_{index:02d}")
    card.name = f"spiral_project_card_{index:02d}_image"
    card.data.materials.clear()
    card.data.materials.append(BELL_MATS[index % len(BELL_MATS)])
    card.hide_viewport = False
    card.hide_render = False
    card.scale.x *= 1.18
    card.scale.y *= 1.18
    card.scale.z *= 1.18

    # Keep old mesh datablocks around only if Blender still references them.
    if old_mesh and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

    rim = bpy.data.objects.new(
        f"jellyfish_{index:02d}_scalloped_orange_rim",
        bpy.data.meshes.new(f"jellyfish_rim_placeholder_{index:02d}"),
    )
    bpy.ops.mesh.primitive_torus_add(major_radius=0.76, minor_radius=0.018, major_segments=96, minor_segments=8)
    torus = bpy.context.object
    torus.name = rim.name
    torus.data.name = f"jellyfish_orange_rim_mesh_{index:02d}"
    torus.data.materials.append(RIM_MAT)
    torus.parent = card
    torus.location = (0, 0, 0.12)

    core_mesh = create_ribbon_mesh(f"jellyfish_core_mesh_{index:02d}", length=1.18, width=0.24, phase=index)
    core = bpy.data.objects.new(f"jellyfish_{index:02d}_warm_inner_frill", core_mesh)
    core.data.materials.append(CORE_MAT)
    add_child(card, core, location=(0.0, 0.0, 0.04), scale=(0.90, 0.90, 0.86))

    for arm in range(5):
        phase = index * 0.7 + arm * 1.1
        mesh = create_ribbon_mesh(
            f"jellyfish_oral_arm_mesh_{index:02d}_{arm:02d}",
            length=1.38 + 0.25 * (arm % 3),
            width=0.10 + 0.025 * (arm % 2),
            phase=phase,
        )
        obj = bpy.data.objects.new(f"jellyfish_{index:02d}_peach_oral_arm_{arm:02d}", mesh)
        obj.data.materials.append(ARM_MAT)
        angle = (arm / 5) * math.pi * 2.0 + index * 0.15
        radius = 0.10 + 0.04 * (arm % 2)
        add_child(
            card,
            obj,
            location=(math.cos(angle) * radius, math.sin(angle) * radius * 0.45, -0.18),
            rotation=(0, 0, math.sin(angle) * 0.16),
            scale=(0.72, 0.92, 0.72),
        )

    for strand in range(18):
        angle = (strand / 18) * math.pi * 2.0 + index * 0.21
        radius = 0.48 + 0.14 * random.random()
        length = 2.5 + 1.1 * random.random()
        points = []
        phase = index * 0.43 + strand * 0.58
        for step in range(7):
            t = step / 6
            points.append(
                Vector(
                    (
                        math.cos(angle) * radius * (1.0 - t * 0.28) + math.sin(t * 5.4 + phase) * 0.10,
                        math.sin(angle) * radius * 0.30 + math.cos(t * 4.8 + phase) * 0.08,
                        -0.10 - t * length,
                    )
                )
            )
        tentacle = make_curve_tentacle(
            f"jellyfish_{index:02d}_fine_tentacle_{strand:02d}",
            points,
            0.0048 if strand % 3 else 0.0065,
            TENTACLE_MAT,
        )
        add_child(card, tentacle)


def replace_cards():
    for obj in list(bpy.data.objects):
        if obj.name.startswith("jellyfish_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    card_images = []
    for obj in list(bpy.data.objects):
        if obj.name.startswith("spiral_project_card_") and obj.name.endswith("_edge"):
            bpy.data.objects.remove(obj, do_unlink=True)
            continue
        match = None
        if obj.name.startswith("spiral_project_card_") and obj.name.endswith("_image"):
            try:
                match = int(obj.name.split("_")[3])
            except (IndexError, ValueError):
                match = None
        if obj.type == "MESH" and match is not None:
            card_images.append((match, obj))

    card_images.sort(key=lambda item: item[0])
    for index, obj in card_images:
        replace_card_with_jellyfish(obj, index)
    return len(card_images)


def save_report(count):
    report_path = OUTPUT / "report.json"
    report = {}
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    report["status"] = "PASS"
    report["workflow"] = "create_jellyfish_cards_scene_pass"
    report["updated"] = datetime.now().isoformat(timespec="seconds")
    report["artifacts"] = {
        "blend": "output/scene.blend",
        "glb": "output/scene.glb",
        "preview": "output/preview.png",
        "source_script": "tools/create_jellyfish_cards_scene_pass.py",
    }
    report["scene_notes"] = [
        "Replaced flat spiral_project_card image meshes with Blender-built jellyfish models.",
        "Deleted flat edge card meshes so the site receives jellyfish as the card anchors.",
        "Jellyfish styling follows the supplied translucent peach/pink/cyan reference.",
    ]
    report["checks"] = [
        f"Replaced {count} card image meshes with jellyfish",
        "Blender file saved",
        "GLB export completed",
        "Preview render completed",
    ]
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    count = replace_cards()
    blend_path = OUTPUT / "scene.blend"
    glb_path = OUTPUT / "scene.glb"
    preview_path = OUTPUT / "preview.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB", export_cameras=True, export_lights=True)
    bpy.context.scene.render.filepath = str(preview_path)
    bpy.ops.render.render(write_still=True)
    save_report(count)
    print(f"[OK] jellyfish_cards={count}")
    print(f"[OK] blend={blend_path}")
    print(f"[OK] glb={glb_path}")
    print(f"[OK] preview={preview_path}")


if __name__ == "__main__":
    main()
