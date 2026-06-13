import json
import math
import random
from datetime import datetime
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
random.seed(202605222)


def input_socket(bsdf, names):
    for name in names:
        socket = bsdf.inputs.get(name)
        if socket:
            return socket
    return None


def make_wet_spine_material():
    mat = bpy.data.materials.get("wet_iridescent_black_metal") or bpy.data.materials.new("wet_iridescent_black_metal")
    mat.use_nodes = True
    mat.blend_method = "OPAQUE"
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        values = {
            ("Base Color",): (0.030, 0.028, 0.052, 1.0),
            ("Metallic",): 0.94,
            ("Roughness",): 0.070,
            ("Emission Color", "Emission"): (0.070, 0.045, 0.145, 1.0),
            ("Emission Strength",): 0.38,
        }
        for names, value in values.items():
            socket = input_socket(bsdf, names)
            if socket:
                socket.default_value = value
    return mat


def vertebra_empties():
    items = [
        obj
        for obj in bpy.data.objects
        if obj.type == "EMPTY" and obj.name.startswith("real_nih_lumbar_vertebra_")
    ]
    items.sort(key=lambda obj: obj.name)
    if not items:
        raise RuntimeError("No repeated NIH vertebra empties found.")
    return items


def cleanup_old_corrected_modifiers(obj):
    for modifier in list(obj.modifiers):
        if modifier.name.startswith("corrected_unit_"):
            obj.modifiers.remove(modifier)


def edit_repeated_unit_mesh(mesh_obj, material):
    mesh_obj.data.materials.clear()
    mesh_obj.data.materials.append(material)
    cleanup_old_corrected_modifiers(mesh_obj)

    # Modify the repeated source part itself, not by adding external plates:
    # subtly compress the copied lumbar unit into a flatter reference-like stack
    # and make the wet surface less perfect.
    mesh = mesh_obj.data
    if not mesh.get("corrected_unit_local_shape_v1"):
        xs = [v.co.x for v in mesh.vertices]
        ys = [v.co.y for v in mesh.vertices]
        zs = [v.co.z for v in mesh.vertices]
        cx = (min(xs) + max(xs)) * 0.5
        cy = (min(ys) + max(ys)) * 0.5
        cz = (min(zs) + max(zs)) * 0.5
        max_x = max(abs(min(xs) - cx), abs(max(xs) - cx), 0.001)
        max_y = max(abs(min(ys) - cy), abs(max(ys) - cy), 0.001)
        max_z = max(abs(min(zs) - cz), abs(max(zs) - cz), 0.001)
        for vertex in mesh.vertices:
            nx = (vertex.co.x - cx) / max_x
            ny = (vertex.co.y - cy) / max_y
            nz = (vertex.co.z - cz) / max_z
            # Reference reads as broad rounded bodies with thinner spacing:
            # flatten only a little and slightly pull side processes outward.
            vertex.co.z = cz + (vertex.co.z - cz) * (0.82 + 0.06 * abs(nx))
            vertex.co.x = cx + (vertex.co.x - cx) * (1.06 + 0.045 * max(0.0, abs(ny) - 0.38))
            vertex.co.y = cy + (vertex.co.y - cy) * (0.94 + 0.035 * abs(nz))
        mesh["corrected_unit_local_shape_v1"] = True
    if not mesh.get("corrected_unit_local_shape_v2"):
        xs = [v.co.x for v in mesh.vertices]
        ys = [v.co.y for v in mesh.vertices]
        zs = [v.co.z for v in mesh.vertices]
        cx = (min(xs) + max(xs)) * 0.5
        cy = (min(ys) + max(ys)) * 0.5
        cz = (min(zs) + max(zs)) * 0.5
        max_x = max(abs(min(xs) - cx), abs(max(xs) - cx), 0.001)
        max_y = max(abs(min(ys) - cy), abs(max(ys) - cy), 0.001)
        max_z = max(abs(min(zs) - cz), abs(max(zs) - cz), 0.001)
        for vertex in mesh.vertices:
            nx = (vertex.co.x - cx) / max_x
            ny = (vertex.co.y - cy) / max_y
            nz = (vertex.co.z - cz) / max_z
            side_process = max(0.0, abs(nx) - 0.48)
            rear_process = max(0.0, abs(ny) - 0.42)
            body_weight = max(0.0, 1.0 - (abs(nx) * 0.68 + abs(ny) * 0.42))
            # The reference reads less like long fins and more like broad,
            # wet vertebral bodies with shorter processes. Pull the extremes
            # inward while giving the central body more vertical mass.
            vertex.co.x = cx + (vertex.co.x - cx) * (1.02 - side_process * 0.34)
            vertex.co.y = cy + (vertex.co.y - cy) * (0.96 - rear_process * 0.18)
            vertex.co.z = cz + (vertex.co.z - cz) * (1.12 + body_weight * 0.10 - abs(nz) * 0.035)
        mesh["corrected_unit_local_shape_v2"] = True
    if not mesh.get("corrected_unit_local_shape_v3"):
        xs = [v.co.x for v in mesh.vertices]
        ys = [v.co.y for v in mesh.vertices]
        zs = [v.co.z for v in mesh.vertices]
        cx = (min(xs) + max(xs)) * 0.5
        cy = (min(ys) + max(ys)) * 0.5
        cz = (min(zs) + max(zs)) * 0.5
        max_x = max(abs(min(xs) - cx), abs(max(xs) - cx), 0.001)
        max_y = max(abs(min(ys) - cy), abs(max(ys) - cy), 0.001)
        max_z = max(abs(min(zs) - cz), abs(max(zs) - cz), 0.001)
        for vertex in mesh.vertices:
            nx = (vertex.co.x - cx) / max_x
            ny = (vertex.co.y - cy) / max_y
            nz = (vertex.co.z - cz) / max_z
            long_tip = max(0.0, abs(nx) - 0.34)
            back_tip = max(0.0, abs(ny) - 0.55)
            central_body = max(0.0, 1.0 - abs(nx) * 0.82 - abs(ny) * 0.36)
            layer_lip = 0.035 * math.sin((nz + 1.0) * math.pi * 2.0)
            vertex.co.x = cx + (vertex.co.x - cx) * (0.98 - long_tip * 0.46)
            vertex.co.y = cy + (vertex.co.y - cy) * (0.99 - back_tip * 0.10)
            vertex.co.z = cz + (vertex.co.z - cz) * (1.08 + central_body * 0.13 + layer_lip)
        mesh["corrected_unit_local_shape_v3"] = True
    if not mesh.get("corrected_unit_local_shape_v4"):
        xs = [v.co.x for v in mesh.vertices]
        ys = [v.co.y for v in mesh.vertices]
        zs = [v.co.z for v in mesh.vertices]
        cx = (min(xs) + max(xs)) * 0.5
        cy = (min(ys) + max(ys)) * 0.5
        cz = (min(zs) + max(zs)) * 0.5
        max_x = max(abs(min(xs) - cx), abs(max(xs) - cx), 0.001)
        max_y = max(abs(min(ys) - cy), abs(max(ys) - cy), 0.001)
        for vertex in mesh.vertices:
            nx = (vertex.co.x - cx) / max_x
            ny = (vertex.co.y - cy) / max_y
            central_body = max(0.0, 1.0 - abs(nx) * 0.74 - abs(ny) * 0.34)
            side_tip = max(0.0, abs(nx) - 0.56)
            # Recover the separated vertebra-disc read after the previous
            # side-profile pass made the copies too tall and merged together.
            vertex.co.z = cz + (vertex.co.z - cz) * (0.46 + central_body * 0.08)
            vertex.co.x = cx + (vertex.co.x - cx) * (1.04 - side_tip * 0.18)
            vertex.co.y = cy + (vertex.co.y - cy) * (1.03 + central_body * 0.06)
        mesh["corrected_unit_local_shape_v4"] = True
    if not mesh.get("corrected_unit_local_shape_v5"):
        xs = [v.co.x for v in mesh.vertices]
        ys = [v.co.y for v in mesh.vertices]
        zs = [v.co.z for v in mesh.vertices]
        cx = (min(xs) + max(xs)) * 0.5
        cy = (min(ys) + max(ys)) * 0.5
        cz = (min(zs) + max(zs)) * 0.5
        max_x = max(abs(min(xs) - cx), abs(max(xs) - cx), 0.001)
        max_y = max(abs(min(ys) - cy), abs(max(ys) - cy), 0.001)
        max_z = max(abs(min(zs) - cz), abs(max(zs) - cz), 0.001)
        for vertex in mesh.vertices:
            nx = (vertex.co.x - cx) / max_x
            ny = (vertex.co.y - cy) / max_y
            nz = (vertex.co.z - cz) / max_z
            central_body = max(0.0, 1.0 - abs(nx) * 0.80 - abs(ny) * 0.50)
            side_process = max(0.0, abs(nx) - 0.46)
            lower_process = max(0.0, -ny - 0.18)
            posterior_process = max(0.0, abs(nz) - 0.36)
            vertex.co.x = cx + (vertex.co.x - cx) * (1.02 + side_process * 0.38 + lower_process * 0.12)
            vertex.co.y = cy + (vertex.co.y - cy) * (0.98 + central_body * 0.08 - lower_process * 0.08)
            vertex.co.z = cz + (vertex.co.z - cz) * (1.00 + posterior_process * 0.18)
        mesh["corrected_unit_local_shape_v5"] = True
    if not mesh.get("corrected_unit_local_shape_v6"):
        xs = [v.co.x for v in mesh.vertices]
        ys = [v.co.y for v in mesh.vertices]
        zs = [v.co.z for v in mesh.vertices]
        cx = (min(xs) + max(xs)) * 0.5
        cy = (min(ys) + max(ys)) * 0.5
        cz = (min(zs) + max(zs)) * 0.5
        max_x = max(abs(min(xs) - cx), abs(max(xs) - cx), 0.001)
        max_y = max(abs(min(ys) - cy), abs(max(ys) - cy), 0.001)
        for vertex in mesh.vertices:
            nx = (vertex.co.x - cx) / max_x
            ny = (vertex.co.y - cy) / max_y
            side = max(0.0, abs(nx) - 0.52)
            face_lip = max(0.0, abs(ny) - 0.58)
            wobble = math.sin(nx * 11.0 + ny * 5.5) * 0.018
            vertex.co.x = cx + (vertex.co.x - cx) * (1.00 + side * 0.10 + wobble)
            vertex.co.y = cy + (vertex.co.y - cy) * (1.02 + face_lip * 0.08 - wobble * 0.5)
        mesh["corrected_unit_local_shape_v6"] = True

    bevel = mesh_obj.modifiers.new("corrected_unit_worn_edges", "BEVEL")
    bevel.width = 0.018
    bevel.segments = 2
    tex = bpy.data.textures.new(f"corrected_unit_pitted_{mesh_obj.name}", "VORONOI")
    tex.noise_scale = 0.72
    tex.intensity = 0.38
    disp = mesh_obj.modifiers.new("corrected_unit_subtle_pitted_surface", "DISPLACE")
    disp.strength = 0.010
    disp.texture = tex
    mesh_obj.modifiers.new("corrected_unit_weighted_normals", "WEIGHTED_NORMAL")


def arrange_repeated_spine(empties):
    count = len(empties)
    visible_count = 12
    top = 6.25
    spacing = 1.06
    sagittal_curve_x = [
        0.42,
        0.24,
        0.02,
        -0.24,
        -0.46,
        -0.54,
        -0.42,
        -0.10,
        0.20,
        0.42,
        0.52,
        0.46,
    ]
    centers = []
    for index, obj in enumerate(empties):
        if index >= visible_count:
            obj.hide_render = True
            obj.hide_viewport = True
            for child in obj.children:
                child.hide_render = True
                child.hide_viewport = True
            continue

        t = index / max(1, visible_count - 1)
        obj.hide_render = False
        obj.hide_viewport = False
        for child in obj.children:
            child.hide_render = False
            child.hide_viewport = False
        # Keep the column made of one repeated part, but arrange the copies
        # into a readable sagittal S curve like the anatomical reference:
        # cervical/lumbar lordosis and thoracic/sacral kyphosis.
        rel = index - (visible_count - 1) * 0.5
        normalized = rel / ((visible_count - 1) * 0.5)
        x = sagittal_curve_x[index] + math.sin(index * 0.72) * 0.018
        y = -0.030 + math.cos(index * 0.7) * 0.014
        z = top - index * spacing
        obj.location = (x, y, z)

        prev_x = sagittal_curve_x[max(0, index - 1)]
        next_x = sagittal_curve_x[min(visible_count - 1, index + 1)]
        tangent_angle = math.degrees(math.atan2(next_x - prev_x, spacing * 2.0))
        per_copy_yaw = rel * 5.6
        yaw = math.radians(-1.5 + per_copy_yaw + math.sin(index * 0.77) * 0.18)
        pitch = math.radians(4.0 - tangent_angle * 2.15 + math.cos(index * 0.51) * 0.22)
        roll = math.radians(-70.0 + math.sin(index * 0.63) * 0.55)
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = (
            Matrix.Rotation(yaw, 4, "Z")
            @ Matrix.Rotation(pitch, 4, "Y")
            @ Matrix.Rotation(roll, 4, "X")
        ).to_euler("XYZ")
        s = 1.08 + math.sin(t * math.pi) * 0.08 + math.sin(index * 1.7) * 0.010
        obj.scale = (s * 1.02, s * 0.48, s * 0.76)
        centers.append((x, y, z))
    return centers


def tune_cards_for_spine_check():
    # This is not a website import. For the sculpt/check pass the cards are
    # hidden so the repeated vertebra column can be judged against references.
    for obj in bpy.data.objects:
        if "spiral_project_card_" in obj.name:
            obj.hide_render = True
            obj.hide_viewport = True


def tune_camera(centers):
    scene = bpy.context.scene
    if scene.camera:
        mid_z = (max(p[2] for p in centers) + min(p[2] for p in centers)) * 0.5
        target = Vector((0.02, -0.02, mid_z + 0.02))
        scene.camera.location = (1.82, -7.05, mid_z + 0.18)
        direction = target - scene.camera.location
        scene.camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.camera.data.lens = 76


def save_report():
    report = {
        "status": "PASS",
        "workflow": "corrected_repeated_vertebra_unit_pass",
        "updated": datetime.now().isoformat(timespec="seconds"),
        "artifacts": {
            "blend": "output/scene.blend",
            "glb": "output/scene.glb",
            "preview": "output/preview.png",
            "source_script": "tools/refine_repeated_vertebra_unit_pass.py",
        },
        "scene_notes": [
            "Corrected approach: edited the repeated NIH vertebra unit itself instead of adding external plate geometry.",
            "Duplicated units now have clearer vertical spacing, slight per-copy rotations, wet iridescent material, and subtle pitted/worn modifiers.",
            "Existing Blender cards are hidden in this sculpt-check render so the spine can be judged against the reference angles.",
        ],
        "checks": ["Blender file saved", "GLB export completed", "Preview render completed"],
    }
    (OUTPUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    material = make_wet_spine_material()
    empties = vertebra_empties()
    for empty in empties:
        empty.hide_render = False
        empty.hide_viewport = False
        for child in empty.children:
            child.hide_render = False
            child.hide_viewport = False
            if child.type == "MESH":
                edit_repeated_unit_mesh(child, material)

    centers = arrange_repeated_spine(empties)
    tune_cards_for_spine_check()
    tune_camera(centers)

    scene = bpy.context.scene
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "High Contrast"
    scene.view_settings.exposure = -0.42
    scene.view_settings.gamma = 1.0

    blend_path = OUTPUT / "scene.blend"
    glb_path = OUTPUT / "scene.glb"
    preview_path = OUTPUT / "preview.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB")
    scene.render.filepath = str(preview_path)
    bpy.ops.render.render(write_still=True)
    save_report()
    print(f"[OK] blend={blend_path}")
    print(f"[OK] glb={glb_path}")
    print(f"[OK] preview={preview_path}")


if __name__ == "__main__":
    main()
