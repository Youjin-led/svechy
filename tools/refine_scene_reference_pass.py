import json
import math
import random
from datetime import datetime
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
random.seed(20260522)


def principled_input(bsdf, names):
    for name in names:
        socket = bsdf.inputs.get(name)
        if socket:
            return socket
    return None


def make_mat(name, base, emission=None, strength=0.0, metallic=0.0, roughness=0.45, alpha=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "BLEND" if alpha < 1.0 else "OPAQUE"
    mat.show_transparent_back = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        color = principled_input(bsdf, ["Base Color"])
        if color:
            color.default_value = base
        metal = principled_input(bsdf, ["Metallic"])
        if metal:
            metal.default_value = metallic
        rough = principled_input(bsdf, ["Roughness"])
        if rough:
            rough.default_value = roughness
        alpha_input = principled_input(bsdf, ["Alpha"])
        if alpha_input:
            alpha_input.default_value = alpha
        if emission:
            e_color = principled_input(bsdf, ["Emission Color", "Emission"])
            e_strength = principled_input(bsdf, ["Emission Strength"])
            if e_color:
                e_color.default_value = emission
            if e_strength:
                e_strength.default_value = strength
    return mat


def cleanup_previous_reference_pass():
    prefixes = (
        "reference_volume_dust_",
        "reference_spine_spark_",
        "reference_depth_ribbon_",
        "reference_spine_halo_",
    )
    for obj in list(bpy.data.objects):
        if obj.name.startswith(prefixes) or obj.name.startswith("hidden_nih_source"):
            bpy.data.objects.remove(obj, do_unlink=True)


def assign_spine_material(mat):
    for obj in bpy.data.objects:
        if obj.type == "MESH" and (
            obj.name.startswith("real_nih_lumbar_vertebra_")
            or obj.name.startswith("hidden_nih_source_")
        ):
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            if not obj.modifiers.get("reference_weighted_normals"):
                obj.modifiers.new("reference_weighted_normals", "WEIGHTED_NORMAL")


def refine_existing_spine():
    empties = [
        obj for obj in bpy.data.objects
        if obj.type == "EMPTY" and obj.name.startswith("real_nih_lumbar_vertebra_")
    ]
    empties.sort(key=lambda obj: obj.name)
    count = len(empties)
    if not count:
        raise RuntimeError("No real NIH vertebra empties found.")

    for index, obj in enumerate(empties):
        t = index / max(1, count - 1)
        z = 7.75 - index * 0.735
        curve = math.sin(t * math.pi * 1.24 - 0.44)
        counter = math.cos(t * math.pi * 1.65 + 0.25)
        obj.location = (curve * 0.20, counter * 0.080 - 0.018, z)
        obj.rotation_euler = (
            math.radians(math.sin(t * math.tau * 1.4) * 3.0),
            math.radians(math.cos(t * math.tau * 1.1) * 4.5),
            math.radians(-24 + index * 2.75 + math.sin(index * 0.73) * 2.0),
        )
        scale = 0.98 + math.sin(t * math.pi) * 0.18 + math.sin(index * 1.7) * 0.018
        obj.scale = (scale, scale, scale)

    return [Vector(obj.location) for obj in empties]


def add_particle(name, loc, radius, mat):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    obj.rotation_euler = (
        random.random() * math.tau,
        random.random() * math.tau,
        random.random() * math.tau,
    )
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    return obj


def add_curve_streak(name, points, mat, thickness):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 8
    curve.bevel_depth = thickness
    curve.bevel_resolution = 2
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for point, loc in zip(spline.bezier_points, points):
        point.co = loc
        point.handle_left_type = "AUTO"
        point.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    obj.data.materials.append(mat)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def build_reference_dust(spine_centers, mats):
    palette = [mats["cyan"], mats["blue"], mats["magenta"], mats["green"], mats["gold"]]
    top = max(p.z for p in spine_centers)
    bottom = min(p.z for p in spine_centers)
    height = top - bottom

    # Dense but real 3D dust around the anatomical column, biased into vertical curtains.
    for i in range(980):
        t = random.random()
        z = bottom + t * height + random.uniform(-0.35, 0.35)
        theta = t * math.tau * 2.35 + random.choice([0.0, 2.05, 4.12]) + random.uniform(-0.42, 0.42)
        radius = random.triangular(0.65, 4.15, 1.65)
        squash = 0.72 + 0.35 * math.sin(t * math.pi)
        loc = (
            math.cos(theta) * radius * 0.88 + random.uniform(-0.18, 0.18),
            math.sin(theta) * radius * 0.42 * squash + random.uniform(-0.12, 0.12) - 0.08,
            z,
        )
        mat = random.choices(palette, weights=[4, 3, 3, 2, 1], k=1)[0]
        size = random.triangular(0.006, 0.034, 0.014)
        add_particle(f"reference_volume_dust_{i:04d}", loc, size, mat)

    # Brighter bead clusters like the references, but placed behind and beside cards.
    clusters = [
        (-2.55, 0.10, 4.9, 1.35, 2.45, 0.62, "magenta"),
        (2.45, -0.18, 3.2, 1.55, 2.75, 0.70, "cyan"),
        (-2.05, 0.24, -2.4, 1.55, 2.55, 0.70, "green"),
        (2.85, -0.12, -4.9, 1.25, 2.2, 0.58, "blue"),
        (0.20, 0.42, 6.6, 3.20, 0.85, 0.60, "magenta"),
    ]
    index = 0
    for cx, cy, cz, sx, sz, sy, key in clusters:
        mat_choices = [mats[key], mats["cyan"], mats["blue"], mats["magenta"]]
        for _ in range(130):
            loc = (
                cx + random.gauss(0, sx * 0.34),
                cy + random.gauss(0, sy * 0.28),
                cz + random.gauss(0, sz * 0.34),
            )
            add_particle(
                f"reference_spine_spark_{index:04d}",
                loc,
                random.triangular(0.008, 0.040, 0.017),
                random.choice(mat_choices),
            )
            index += 1

    # Thin curved light trails made from actual curves, not flat planes.
    for band in range(9):
        phase = band * 0.55
        z0 = bottom + random.random() * height
        points = []
        for step in range(7):
            t = step / 6
            z = z0 + (t - 0.5) * random.uniform(1.2, 3.4)
            theta = phase + t * math.tau * random.uniform(0.28, 0.48)
            r = random.uniform(2.4, 4.9)
            points.append(Vector((math.cos(theta) * r, math.sin(theta) * r * 0.42 - 0.10, z)))
        add_curve_streak(
            f"reference_depth_ribbon_{band:02d}",
            points,
            random.choice([mats["cyan_soft"], mats["magenta_soft"], mats["green_soft"]]),
            random.uniform(0.002, 0.005),
        )


def tune_lighting():
    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            if "cyan" in obj.name.lower() or "softbox" in obj.name.lower():
                obj.data.energy *= 1.16
            if "magenta" in obj.name.lower() or "pink" in obj.name.lower():
                obj.data.energy *= 1.28
            if "green" in obj.name.lower():
                obj.data.energy *= 1.20

    bpy.ops.object.light_add(type="POINT", location=(-1.15, -2.05, 4.1))
    glint = bpy.context.object
    glint.name = "reference_spine_halo_cyan"
    glint.data.energy = 460
    glint.data.color = (0.02, 0.80, 1.0)

    bpy.ops.object.light_add(type="POINT", location=(1.45, -1.75, -1.8))
    magenta = bpy.context.object
    magenta.name = "reference_spine_halo_magenta"
    magenta.data.energy = 360
    magenta.data.color = (1.0, 0.15, 0.72)


def save_report():
    report = {
        "status": "PASS",
        "workflow": "refine_existing_blender_scene_reference_pass",
        "updated": datetime.now().isoformat(timespec="seconds"),
        "artifacts": {
            "blend": "output/scene.blend",
            "glb": "output/scene.glb",
            "preview": "output/preview.png",
            "source_script": "tools/refine_scene_reference_pass.py",
        },
        "scene_notes": [
            "Refined the existing real NIH vertebra column instead of adding a separate procedural spine.",
            "Added visible 3D dust as small mesh particles and curve streaks inside Blender, avoiding flat 2D particle cards.",
            "Kept a checkpoint and scene attempt before modification so the previous scene can be restored.",
        ],
        "checks": [
            "Blender file saved",
            "GLB export completed",
            "Preview render completed",
        ],
    }
    (OUTPUT / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    cleanup_previous_reference_pass()

    spine_mat = make_mat(
        "wet_iridescent_black_metal",
        (0.035, 0.040, 0.075, 1.0),
        emission=(0.040, 0.070, 0.145, 1.0),
        strength=0.42,
        metallic=0.92,
        roughness=0.105,
    )
    mats = {
        "cyan": make_mat("reference_particle_cyan", (0.0, 0.62, 0.92, 1), (0.0, 0.86, 1.0, 1), 2.4, roughness=0.2),
        "blue": make_mat("reference_particle_blue", (0.05, 0.18, 0.84, 1), (0.10, 0.32, 1.0, 1), 1.9, roughness=0.22),
        "magenta": make_mat("reference_particle_magenta", (0.78, 0.12, 0.64, 1), (1.0, 0.12, 0.80, 1), 2.1, roughness=0.24),
        "green": make_mat("reference_particle_green", (0.0, 0.78, 0.32, 1), (0.0, 0.95, 0.36, 1), 1.9, roughness=0.22),
        "gold": make_mat("reference_particle_gold", (1.0, 0.62, 0.28, 1), (1.0, 0.50, 0.10, 1), 1.3, roughness=0.28),
        "cyan_soft": make_mat("reference_ribbon_cyan_soft", (0.04, 0.58, 0.90, 0.20), (0.04, 0.70, 1.0, 1), 0.36, alpha=0.20),
        "magenta_soft": make_mat("reference_ribbon_magenta_soft", (0.70, 0.14, 0.66, 0.16), (0.95, 0.12, 0.80, 1), 0.30, alpha=0.16),
        "green_soft": make_mat("reference_ribbon_green_soft", (0.05, 0.78, 0.35, 0.14), (0.0, 0.9, 0.38, 1), 0.26, alpha=0.14),
    }

    assign_spine_material(spine_mat)
    spine_centers = refine_existing_spine()
    build_reference_dust(spine_centers, mats)
    tune_lighting()

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
