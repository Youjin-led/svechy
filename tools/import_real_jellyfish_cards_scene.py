import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
SOURCE_BLEND = OUTPUT / "attempts" / "20260524-210050-before-s-curve-spine-posture" / "scene.blend"
JELLYFISH_ASSET = Path(sys.argv[-1])

random.seed(202605264)


def clear_selection():
    for obj in bpy.context.scene.objects:
        obj.select_set(False)


def material_socket(bsdf, names):
    for name in names:
        socket = bsdf.inputs.get(name)
        if socket:
            return socket
    return None


def set_socket(bsdf, names, value):
    socket = material_socket(bsdf, names)
    if socket:
        socket.default_value = value


def make_glow_material(name, color, alpha, emission, strength, roughness=0.28):
    mat = bpy.data.materials.new(name)
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
        set_socket(bsdf, ("Emission Color", "Emission"), emission)
        set_socket(bsdf, ("Emission Strength",), strength)
    mat.diffuse_color = color
    return mat


def bake_world_mesh(obj, root_min, root_center_xy, scale):
    mesh = obj.data
    verts = []
    for vert in mesh.vertices:
        world = obj.matrix_world @ vert.co
        local = Vector((
            (world.x - root_center_xy.x) * scale,
            (world.y - root_center_xy.y) * scale,
            (world.z - root_min.z) * scale,
        ))
        verts.append(local)
    faces = [[v for v in poly.vertices] for poly in mesh.polygons]
    baked = bpy.data.meshes.new(f"jellyfish_real_{obj.data.name}")
    baked.from_pydata([tuple(v) for v in verts], [], faces)
    baked.update()
    return baked


def import_template():
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(JELLYFISH_ASSET))
    imported = [obj for obj in bpy.context.scene.objects if obj not in before]
    mesh_objects = [obj for obj in imported if obj.type == "MESH"]
    if not mesh_objects:
        raise RuntimeError(f"No mesh objects imported from {JELLYFISH_ASSET}")

    root_min = Vector((10**9, 10**9, 10**9))
    root_max = Vector((-10**9, -10**9, -10**9))
    for obj in mesh_objects:
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            root_min.x = min(root_min.x, world.x)
            root_min.y = min(root_min.y, world.y)
            root_min.z = min(root_min.z, world.z)
            root_max.x = max(root_max.x, world.x)
            root_max.y = max(root_max.y, world.y)
            root_max.z = max(root_max.z, world.z)

    size = root_max - root_min
    scale = 1.0 / max(size.x, size.y, size.z)
    center_xy = Vector(((root_min.x + root_max.x) * 0.5, (root_min.y + root_max.y) * 0.5, 0))

    template = []
    for obj in sorted(mesh_objects, key=lambda item: item.name):
        template.append({
            "name": obj.name,
            "mesh": bake_world_mesh(obj, root_min, center_xy, scale),
        })

    for obj in imported:
        bpy.data.objects.remove(obj, do_unlink=True)
    return template


def add_card_jellyfish(card, index, template, materials):
    # The imported model is a vertical creature. Reuse the old card mesh as the
    # rail/hover anchor, but replace its geometry with the jellyfish bell.
    bell_entry = max(template, key=lambda entry: len(entry["mesh"].vertices))
    tentacle_entries = [entry for entry in template if entry is not bell_entry]

    old_data = card.data
    card.data = bell_entry["mesh"].copy()
    card.data.name = f"jellyfish_real_bell_mesh_{index:02d}"
    card.name = f"spiral_project_card_{index:02d}_image"
    card.data.materials.clear()
    card.data.materials.append(materials["bell"][index % len(materials["bell"])])
    card.scale = (1.55, 1.55, 1.55)
    card.hide_viewport = False
    card.hide_render = False
    card["asset_source"] = str(JELLYFISH_ASSET)
    animate_jellyfish_bell(card, index)
    if old_data and old_data.users == 0:
        bpy.data.meshes.remove(old_data)

    for entry_i, entry in enumerate(tentacle_entries):
        child = bpy.data.objects.new(
            f"jellyfish_{index:02d}_real_tentacles_{entry_i:02d}",
            entry["mesh"],
        )
        child.data.materials.append(materials["tentacles"])
        child.parent = card
        child.location = (0, 0, 0)
        child.rotation_euler = (0, 0, 0)
        child.scale = (1, 1, 1)
        bpy.context.collection.objects.link(child)
        animate_jellyfish_tentacles(child, index, entry_i)


def contracted_bell_position(co, bounds):
    height = max(bounds["max_z"] - bounds["min_z"], 0.001)
    v = max(0.0, min(1.0, (co.z - bounds["min_z"]) / height))
    rim = 1.0 - v
    rim_pull = rim ** 1.55
    crown = v ** 2.0
    return Vector((
        co.x * (1.0 - (0.18 + rim_pull * 0.58)),
        co.y * (1.0 - (0.16 + rim_pull * 0.44)),
        co.z + (rim_pull * 0.20 - crown * 0.045),
    ))


def animate_jellyfish_bell(card, index):
    mesh = card.data
    basis = card.shape_key_add(name="Basis")
    contracted = card.shape_key_add(name="bell_contract")
    mesh.update()
    bounds = {
        "min_z": min(vertex.co.z for vertex in mesh.vertices),
        "max_z": max(vertex.co.z for vertex in mesh.vertices),
    }
    for i, vertex in enumerate(mesh.vertices):
        contracted.data[i].co = contracted_bell_position(vertex.co, bounds)

    cycle = 64 + (index % 4) * 4
    start = 1 + index * 5
    keys = [
        (start, 0.0),
        (start + 8, 1.0),
        (start + 22, 0.0),
        (start + cycle, 0.0),
    ]
    shape_key = mesh.shape_keys.key_blocks["bell_contract"]
    for frame, value in keys:
        shape_key.value = value
        shape_key.keyframe_insert("value", frame=frame)
    if mesh.shape_keys.animation_data and mesh.shape_keys.animation_data.action:
        action = mesh.shape_keys.animation_data.action
        action.name = f"jellyfish_swim_{index:02d}_bell"


def animate_jellyfish_tentacles(child, index, entry_i):
    mesh = child.data
    phase = index * 0.37 + entry_i * 0.51
    if not mesh.get("shared_water_wave_ready"):
        setup_shared_tentacle_wave(child)

    cycle = 64 + (index % 4) * 4
    start = 1 + index * 5
    keys = [
        (start, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
        (start + 8, (math.sin(phase) * 0.010, -0.012, 0.012), (-0.026, math.cos(phase) * 0.018, math.sin(phase) * 0.020), (1.0, 1.0, 1.018)),
        (start + 18, (math.sin(phase + 0.9) * 0.024, -0.006, -0.020), (-0.050, math.cos(phase + 0.4) * 0.028, math.sin(phase + 0.6) * 0.034), (1.0, 1.0, 1.035)),
        (start + 34, (math.sin(phase + 1.7) * 0.032, 0.012, -0.032), (0.030, math.cos(phase + 1.1) * 0.038, -0.024), (1.0, 1.0, 1.010)),
        (start + 50, (math.sin(phase + 2.6) * 0.020, 0.018, -0.016), (0.018, math.cos(phase + 2.0) * 0.026, 0.026), (1.0, 1.0, 0.992)),
        (start + cycle, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
    ]
    for frame, location, rotation, scale in keys:
        child.location = location
        child.rotation_euler = rotation
        child.scale = scale
        child.keyframe_insert("location", frame=frame)
        child.keyframe_insert("rotation_euler", frame=frame)
        child.keyframe_insert("scale", frame=frame)
    if child.animation_data and child.animation_data.action:
        action = child.animation_data.action
        action.name = f"jellyfish_swim_{index:02d}_tentacles_{entry_i:02d}"


def setup_shared_tentacle_wave(child):
    mesh = child.data
    if not mesh.shape_keys:
        child.shape_key_add(name="Basis")
    if "water_wave_left" not in mesh.shape_keys.key_blocks:
        wave_left = child.shape_key_add(name="water_wave_left")
        wave_right = child.shape_key_add(name="water_wave_right")
        impulse = child.shape_key_add(name="bell_impulse_lag")
        mesh.update()
        min_z = min(vertex.co.z for vertex in mesh.vertices)
        max_z = max(vertex.co.z for vertex in mesh.vertices)
        height = max(max_z - min_z, 0.001)
        for i, vertex in enumerate(mesh.vertices):
            co = vertex.co
            from_tip = max(0.0, min(1.0, (max_z - co.z) / height))
            free = from_tip ** 1.35
            root_lock = max(0.0, min(1.0, (from_tip - 0.08) / 0.92))
            lateral = (0.030 + free * 0.115) * root_lock
            trailing = (0.018 + free * 0.090) * root_lock
            lift = free * 0.055
            wave_left.data[i].co = Vector((
                co.x + lateral * math.sin(from_tip * math.pi * 2.35),
                co.y + trailing * math.sin(from_tip * math.pi * 3.25),
                co.z - lift * 0.38,
            ))
            wave_right.data[i].co = Vector((
                co.x - lateral * math.sin(from_tip * math.pi * 2.10 + 0.75),
                co.y - trailing * math.sin(from_tip * math.pi * 3.55 + 0.40),
                co.z - lift * 0.55,
            ))
            impulse.data[i].co = Vector((
                co.x + math.sin(from_tip * 5.1) * lateral * 0.36,
                co.y + math.cos(from_tip * 4.8) * trailing * 0.30,
                co.z + lift * 1.04,
            ))

    shape_keys = mesh.shape_keys.key_blocks
    shape_key_frames = [
        (1, 0.0, 0.0, 0.0),
        (7, 0.0, 0.0, 0.80),
        (15, 0.32, 0.0, 0.28),
        (28, 0.86, 0.0, 0.0),
        (43, 0.08, 0.72, 0.0),
        (57, 0.0, 0.36, 0.0),
        (66, 0.0, 0.0, 0.0),
    ]
    for frame, left, right, lag in shape_key_frames:
        shape_keys["water_wave_left"].value = left
        shape_keys["water_wave_right"].value = right
        shape_keys["bell_impulse_lag"].value = lag
        shape_keys["water_wave_left"].keyframe_insert("value", frame=frame)
        shape_keys["water_wave_right"].keyframe_insert("value", frame=frame)
        shape_keys["bell_impulse_lag"].keyframe_insert("value", frame=frame)
    if mesh.shape_keys.animation_data and mesh.shape_keys.animation_data.action:
        action = mesh.shape_keys.animation_data.action
        action.name = "jellyfish_shared_tentacle_water_wave"
    mesh["shared_water_wave_ready"] = True


def replace_cards(template):
    materials = {
        "bell": [
            make_glow_material("jellyfish_real_bell_cyan_glass", (0.56, 0.94, 1.0, 0.58), 0.58, (0.22, 0.68, 0.95, 1), 0.55),
            make_glow_material("jellyfish_real_bell_lilac_glass", (0.88, 0.62, 1.0, 0.58), 0.58, (0.62, 0.26, 0.9, 1), 0.50),
            make_glow_material("jellyfish_real_bell_rose_glass", (1.0, 0.55, 0.76, 0.60), 0.60, (1.0, 0.22, 0.55, 1), 0.52),
        ],
        "tentacles": make_glow_material("jellyfish_real_orange_tentacles", (1.0, 0.42, 0.24, 0.82), 0.82, (1.0, 0.23, 0.12, 1), 0.95),
    }

    for obj in list(bpy.data.objects):
        if obj.name.startswith("jellyfish_"):
            bpy.data.objects.remove(obj, do_unlink=True)
        elif obj.name.startswith("spiral_project_card_") and obj.name.endswith("_edge"):
            bpy.data.objects.remove(obj, do_unlink=True)

    cards = []
    for obj in bpy.context.scene.objects:
        match = obj.name.split("_")
        if obj.type == "MESH" and obj.name.startswith("spiral_project_card_") and obj.name.endswith("_image"):
            try:
                index = int(match[3])
            except (IndexError, ValueError):
                continue
            cards.append((index, obj))

    for index, card in sorted(cards):
        add_card_jellyfish(card, index, template, materials)

    print("REPLACED_CARD_COUNT", len(cards))


def main():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    template = import_template()
    print("REAL_JELLYFISH_TEMPLATE_PARTS", [entry["name"] for entry in template])
    replace_cards(template)

    # Mark provenance in a tiny text datablock; useful later when the question is
    # "where did this model come from?"
    text = bpy.data.texts.new("REAL_JELLYFISH_ASSET_SOURCE")
    text.write(f"Imported from {JELLYFISH_ASSET}\n")
    text.write("Page: https://www.get3dmodels.com/creatures/rainbow-jellyfish/\n")

    OUTPUT.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT / "scene.blend"))
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT / "scene.glb"),
        export_format="GLB",
        export_cameras=True,
        export_lights=True,
        export_animations=True,
    )
    print("SAVED", OUTPUT / "scene.blend", OUTPUT / "scene.glb")


if __name__ == "__main__":
    main()
