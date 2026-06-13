from __future__ import annotations

import math
import random
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT.parents[1] / "3д художник" / "blender-mcp-work" / "output"
SOURCE_BLEND = EXTERNAL / "active_theory_work_page_scene.blend"
OUTPUT = EXTERNAL
BLEND_PATH = OUTPUT / "active_theory_work_page_scene_refined.blend"
GLB_PATH = OUTPUT / "active_theory_work_page_scene_refined.glb"
PREVIEW_PATH = OUTPUT / "active_theory_work_page_refined_preview.png"
REFERENCE_IMAGES = [
    Path(r"c:\Users\Ардор\OneDrive\Изображения\Screenshots\Снимок экрана 2026-05-14 130627.png"),
    Path(r"c:\Users\Ардор\OneDrive\Изображения\Screenshots\Снимок экрана 2026-05-14 133450.png"),
    Path(r"c:\Users\Ардор\OneDrive\Изображения\Screenshots\Снимок экрана 2026-05-14 133501.png"),
    Path(r"c:\Users\Ардор\OneDrive\Изображения\Screenshots\Снимок экрана 2026-05-14 133518.png"),
    Path(r"c:\Users\Ардор\OneDrive\Изображения\Screenshots\Снимок экрана 2026-05-14 133527.png"),
    Path(r"c:\Users\Ардор\OneDrive\Изображения\Screenshots\Снимок экрана 2026-05-14 133541.png"),
]

EXTERNAL = ROOT.parents[1] / "3\u0434 \u0445\u0443\u0434\u043e\u0436\u043d\u0438\u043a" / "blender-mcp-work" / "output"
SOURCE_BLEND = EXTERNAL / "active_theory_work_page_scene.blend"
OUTPUT = EXTERNAL
BLEND_PATH = OUTPUT / "active_theory_work_page_scene_refined.blend"
GLB_PATH = OUTPUT / "active_theory_work_page_scene_refined.glb"
PREVIEW_PATH = OUTPUT / "active_theory_work_page_refined_preview.png"
SCREENSHOT_DIR = Path.home() / "OneDrive" / "\u0418\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u044f" / "Screenshots"
REFERENCE_IMAGES = [
    SCREENSHOT_DIR / "\u0421\u043d\u0438\u043c\u043e\u043a \u044d\u043a\u0440\u0430\u043d\u0430 2026-05-14 130627.png",
    SCREENSHOT_DIR / "\u0421\u043d\u0438\u043c\u043e\u043a \u044d\u043a\u0440\u0430\u043d\u0430 2026-05-14 133450.png",
    SCREENSHOT_DIR / "\u0421\u043d\u0438\u043c\u043e\u043a \u044d\u043a\u0440\u0430\u043d\u0430 2026-05-14 133501.png",
    SCREENSHOT_DIR / "\u0421\u043d\u0438\u043c\u043e\u043a \u044d\u043a\u0440\u0430\u043d\u0430 2026-05-14 133518.png",
    SCREENSHOT_DIR / "\u0421\u043d\u0438\u043c\u043e\u043a \u044d\u043a\u0440\u0430\u043d\u0430 2026-05-14 133527.png",
    SCREENSHOT_DIR / "\u0421\u043d\u0438\u043c\u043e\u043a \u044d\u043a\u0440\u0430\u043d\u0430 2026-05-14 133541.png",
]

random.seed(514133)


def material(name, color, alpha=1.0, emission=None, strength=0.0, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    mat.show_transparent_back = True
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Alpha"].default_value = alpha
        bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if emission and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def image_material(name, image_path, alpha=0.72, strength=0.65):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    mat.show_transparent_back = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    image = bpy.data.images.load(str(image_path), check_existing=True)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = image
    tex.extension = "CLIP"
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = strength
    output = nodes.get("Material Output")
    mat.node_tree.links.new(tex.outputs["Color"], emission.inputs["Color"])
    mix.inputs[0].default_value = alpha
    mat.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
    mat.node_tree.links.new(emission.outputs[0], mix.inputs[2])
    mat.node_tree.links.new(mix.outputs[0], output.inputs["Surface"])
    if bsdf:
        nodes.remove(bsdf)
    mat.diffuse_color = (0.45, 0.72, 0.78, alpha)
    return mat


def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def move_to(obj, col):
    for existing in list(obj.users_collection):
        existing.objects.unlink(obj)
    col.objects.link(obj)


def add_cube(name, loc, scale, mat, col, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    obj.show_transparent = True
    if bevel:
        mod = obj.modifiers.new(f"{name}_rounded_edges", "BEVEL")
        mod.width = bevel
        mod.segments = 18
        obj.modifiers.new(f"{name}_weighted_normals", "WEIGHTED_NORMAL")
    move_to(obj, col)
    return obj


def add_text(name, body, loc, size, mat, col, align="CENTER"):
    bpy.ops.object.text_add(location=loc, rotation=(0, math.radians(180), 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = body
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.008
    obj.data.space_character = 1.28
    obj.data.space_line = 0.72
    obj.data.materials.append(mat)
    move_to(obj, col)
    return obj


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_glitch_text(name, body, loc, size, mat, cyan, magenta, col, align="CENTER"):
    add_text(f"{name}_white", body, loc, size, mat, col, align=align)
    add_text(f"{name}_cyan_offset", body, (loc[0] - 0.035, loc[1] + 0.012, loc[2] - 0.018), size, cyan, col, align=align)
    add_text(f"{name}_magenta_offset", body, (loc[0] + 0.035, loc[1] - 0.012, loc[2] - 0.026), size, magenta, col, align=align)


def add_reference_card(index, title, loc, scale, tint, text_size, col, mats, align="CENTER"):
    card = add_cube(
        f"Reference_Foreground_Card_{index:02d}",
        loc,
        scale,
        tint,
        col,
        rot=(0, 0, math.radians(random.uniform(-1.4, 1.4))),
        bevel=0.22,
    )
    front_z = loc[2] - 0.12

    add_cube(
        f"Reference_Foreground_Card_{index:02d}_rim",
        (loc[0], loc[1], front_z - 0.012),
        (scale[0] * 1.015, scale[1] * 1.015, 0.018),
        mats["rim_cyan"] if index % 2 else mats["rim_violet"],
        col,
        bevel=0.24,
    )

    for i in range(9):
        add_cube(
            f"Reference_Card_{index:02d}_smear_{i:02d}",
            (
                loc[0] + random.uniform(-scale[0] * 0.65, scale[0] * 0.65),
                loc[1] + random.uniform(-scale[1] * 0.52, scale[1] * 0.52),
                front_z - 0.035 - i * 0.002,
            ),
            (random.uniform(0.24, 0.78), random.uniform(0.05, 0.24), 0.006),
            random.choice([mats["smear_cyan"], mats["smear_violet"], mats["smear_green"], mats["smear_grey"]]),
            col,
            rot=(0, 0, math.radians(random.uniform(-14, 14))),
            bevel=0.02,
        )

    if index == 1:
        add_glitch_text(
            f"Reference_Card_{index:02d}_title",
            title,
            (loc[0] - scale[0] * 0.18, loc[1] + 0.02, front_z - 0.095),
            text_size,
            mats["text_white"],
            mats["text_cyan"],
            mats["text_magenta"],
            col,
            align=align,
        )
    else:
        add_glitch_text(
            f"Reference_Card_{index:02d}_title",
            title,
            (loc[0], loc[1] + 0.03, front_z - 0.095),
            text_size,
            mats["text_white"],
            mats["text_cyan"],
            mats["text_magenta"],
            col,
            align=align,
        )

    for row in range(5):
        add_cube(
            f"Reference_Card_{index:02d}_glitch_bar_{row:02d}",
            (
                loc[0] + scale[0] * random.uniform(0.18, 0.78),
                loc[1] - scale[1] * 0.24 - row * 0.16,
                front_z - 0.13,
            ),
            (random.uniform(0.28, 0.74), 0.012, 0.006),
            random.choice([mats["text_cyan"], mats["text_magenta"], mats["text_white"]]),
            col,
            bevel=0.002,
        )
    return card


def add_reference_image_card(index, image_path, loc, scale, col, mats, title=None, text_size=0.34):
    frame = add_cube(
        f"Reference_Image_Card_{index:02d}_GlassBody",
        loc,
        scale,
        mats["image_glass"],
        col,
        rot=(0, 0, math.radians(random.uniform(-0.9, 0.9))),
        bevel=0.22,
    )
    mat = image_material(f"REF_Image_Texture_{index:02d}", image_path, alpha=0.94, strength=0.56)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(loc[0], loc[1], loc[2] - 0.105), rotation=(0, math.radians(180), 0))
    plane = bpy.context.object
    plane.name = f"Reference_Image_Card_{index:02d}_ScreenshotSurface"
    plane.scale = (scale[0] * 0.96, scale[1] * 0.96, 1)
    plane.data.materials.append(mat)
    move_to(plane, col)
    add_cube(
        f"Reference_Image_Card_{index:02d}_CyanRim",
        (loc[0], loc[1], loc[2] - 0.13),
        (scale[0] * 1.015, scale[1] * 1.015, 0.012),
        mats["rim_cyan"] if index % 2 else mats["rim_violet"],
        col,
        bevel=0.24,
    )
    if title:
        add_glitch_text(
            f"Reference_Image_Card_{index:02d}_OverlayTitle",
            title,
            (loc[0], loc[1] + 0.02, loc[2] - 0.2),
            text_size,
            mats["text_white"],
            mats["text_cyan"],
            mats["text_magenta"],
            col,
        )
    return frame


def add_particle_clouds(col, mats):
    palette = [mats["dot_cyan"], mats["dot_violet"], mats["dot_green"], mats["dot_pink"], mats["dot_warm"]]
    clusters = [(-2.1, 2.9, -4.45), (1.8, 1.4, -4.5), (-0.4, -1.8, -4.35), (3.8, 3.3, -4.55), (-4.2, -2.0, -4.5)]
    for cluster_index, (cx, cy, cz) in enumerate(clusters):
        for i in range(120):
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8,
                ring_count=4,
                radius=random.uniform(0.006, 0.024),
                location=(
                    cx + random.gauss(0, 0.62),
                    cy + random.gauss(0, 0.88),
                    cz + random.gauss(0, 0.22),
                ),
            )
            obj = bpy.context.object
            obj.name = f"Reference_Colored_Dust_{cluster_index:02d}_{i:03d}"
            obj.data.materials.append(random.choice(palette))
            move_to(obj, col)


def add_organic_spine(col, mats):
    for i in range(17):
        y = -3.75 + i * 0.47
        x = math.sin(i * 0.72) * 0.12
        z = -5.45 + math.cos(i * 0.51) * 0.08
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=48,
            ring_count=24,
            radius=random.uniform(0.36, 0.56),
            location=(x, y, z),
            rotation=(random.random() * math.pi, random.random() * math.pi, random.random() * math.pi),
        )
        obj = bpy.context.object
        obj.name = f"Reference_Iridescent_Spine_Node_{i:02d}"
        obj.scale = (random.uniform(0.92, 1.24), random.uniform(0.62, 0.94), random.uniform(0.38, 0.66))
        obj.data.materials.append(mats["spine_chrome"])
        obj.modifiers.new(f"{obj.name}_weighted_normals", "WEIGHTED_NORMAL")
        try:
            for polygon in obj.data.polygons:
                polygon.use_smooth = True
        except Exception:
            pass
        move_to(obj, col)

        for side in (-1, 1):
            if random.random() < 0.78:
                bpy.ops.mesh.primitive_uv_sphere_add(
                    segments=32,
                    ring_count=16,
                    radius=random.uniform(0.18, 0.34),
                    location=(x + side * random.uniform(0.45, 0.78), y + random.uniform(-0.09, 0.12), z + random.uniform(-0.04, 0.08)),
                    rotation=(0, math.radians(22 * side), math.radians(random.uniform(-14, 14))),
                )
                spike = bpy.context.object
                spike.name = f"Reference_Iridescent_Spine_Lobe_{i:02d}_{side:+d}"
                spike.scale = (random.uniform(1.5, 2.4), random.uniform(0.34, 0.55), random.uniform(0.22, 0.38))
                spike.data.materials.append(mats["spine_chrome"])
                spike.modifiers.new(f"{spike.name}_weighted_normals", "WEIGHTED_NORMAL")
                for polygon in spike.data.polygons:
                    polygon.use_smooth = True
                move_to(spike, col)


def add_reference_ui(col, mats):
    add_cube("Reference_Top_Right_Pill", (5.35, 4.02, -7.2), (1.5, 0.26, 0.025), mats["ui_glass"], col, bevel=0.12)
    add_text("Reference_Top_Right_Work", "WORK", (4.58, 3.97, -7.28), 0.135, mats["text_white"], col)
    add_cube("Reference_Top_Right_Line", (5.28, 3.97, -7.29), (0.34, 0.006, 0.006), mats["text_white"], col, bevel=0.002)
    add_text("Reference_Top_Right_Contact", "CONTACT", (6.01, 3.97, -7.28), 0.135, mats["text_white"], col)
    add_cube("Reference_Top_Right_Glow", (5.65, 3.65, -7.36), (0.78, 0.025, 0.012), mats["lime_glow"], col, bevel=0.02)

    add_text("Reference_Filter_Title", "WHAT ARE YOU LOOKING FOR?", (-5.55, -3.22, -7.26), 0.13, mats["text_white"], col, align="LEFT")
    for i, label in enumerate(["-> WEBSITES", "-> INSTALLATIONS", "-> XR / VR / AI", "-> MULTIPLAYER", "-> GAMES"]):
        add_text(f"Reference_Filter_{i:02d}", label, (-5.55, -3.56 - i * 0.31, -7.27), 0.13, mats["text_violet"], col, align="LEFT")
    add_cube("Reference_Ask_Pill", (-4.76, -5.2, -7.25), (0.84, 0.19, 0.02), mats["ask_glass"], col, bevel=0.10)
    add_text("Reference_Ask_Text", "ASK ME ANYTHING...", (-4.76, -5.24, -7.3), 0.105, mats["text_violet_dim"], col)


def add_film_grain(col, mats):
    for i in range(900):
        add_cube(
            f"Reference_Film_Grain_{i:03d}",
            (random.uniform(-6.4, 6.4), random.uniform(-5.1, 5.1), -7.45),
            (random.uniform(0.006, 0.016), random.uniform(0.006, 0.016), 0.002),
            random.choice([mats["grain_dark"], mats["grain_light"], mats["grain_violet"]]),
            col,
        )


def revise_camera_and_render():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1840
    scene.render.resolution_y = 900
    scene.eevee.taa_render_samples = 48
    if hasattr(scene.eevee, "use_bloom"):
        scene.eevee.use_bloom = True
        scene.eevee.bloom_intensity = 0.24
        scene.eevee.bloom_radius = 5.2
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "High Contrast"
    scene.view_settings.exposure = -0.7

    cam = bpy.data.objects.get("Camera_Preview_Front")
    if cam is None:
        bpy.ops.object.camera_add(location=(0, -1.2, -18))
        cam = bpy.context.object
    cam.name = "Camera_Reference_Close_Work_Page"
    cam.data.type = "ORTHO"
    cam.location = (0, -1.2, -18)
    cam.data.ortho_scale = 9.8
    look_at(cam, (0, -1.5, 0))
    scene.camera = cam

    scene.render.filepath = str(PREVIEW_PATH)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.ops.export_scene.gltf(filepath=str(GLB_PATH), export_format="GLB", export_cameras=True, export_lights=True)
    bpy.ops.render.render(write_still=True)


def main():
    if not SOURCE_BLEND.exists():
        raise FileNotFoundError(SOURCE_BLEND)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    col = collection("08_Reference_Refinement")

    for obj in bpy.data.objects:
        if obj.type not in {"CAMERA", "LIGHT"}:
            obj.hide_render = True
            obj.hide_viewport = True

    mats = {
        "glass_left": material("REF_Glass_Left", (0.18, 0.25, 0.27, 0.42), 0.42, (0.03, 0.12, 0.13, 1), 0.12, 0.82, 0.08),
        "glass_right": material("REF_Glass_Right", (0.025, 0.045, 0.05, 0.58), 0.58, (0.02, 0.08, 0.09, 1), 0.12, 0.68, 0.12),
        "glass_center": material("REF_Glass_Center", (0.08, 0.16, 0.17, 0.48), 0.48, (0.02, 0.10, 0.13, 1), 0.14, 0.72, 0.1),
        "image_glass": material("REF_Image_Glass_Backplate", (0.05, 0.10, 0.11, 0.42), 0.42, (0.02, 0.12, 0.15, 1), 0.16, 0.74, 0.08),
        "spine_chrome": material("REF_Iridescent_Black_Chrome", (0.035, 0.045, 0.065, 0.96), 0.96, (0.14, 0.07, 0.24, 1), 0.35, 0.28, 0.84),
        "rim_cyan": material("REF_Rim_Cyan", (0.1, 0.85, 0.95, 0.36), 0.36, (0.0, 0.85, 1, 1), 0.8),
        "rim_violet": material("REF_Rim_Violet", (0.56, 0.28, 0.96, 0.28), 0.28, (0.52, 0.1, 1, 1), 0.75),
        "smear_cyan": material("REF_Smear_Cyan", (0.15, 0.92, 1, 0.20), 0.20, (0.05, 0.55, 0.75, 1), 0.35),
        "smear_violet": material("REF_Smear_Violet", (0.75, 0.25, 1, 0.18), 0.18, (0.55, 0.12, 0.9, 1), 0.42),
        "smear_green": material("REF_Smear_Green", (0.25, 0.85, 0.48, 0.14), 0.14, (0.12, 0.55, 0.26, 1), 0.24),
        "smear_grey": material("REF_Smear_Grey", (0.72, 0.78, 0.72, 0.12), 0.12, (0.18, 0.24, 0.23, 1), 0.12),
        "text_white": material("REF_Text_White", (0.88, 0.96, 1.0, 1), 1, (0.75, 0.94, 1, 1), 1.45),
        "text_cyan": material("REF_Text_Cyan", (0.0, 0.95, 1.0, 0.75), 0.75, (0.0, 0.9, 1, 1), 1.65),
        "text_magenta": material("REF_Text_Magenta", (1.0, 0.2, 0.72, 0.70), 0.70, (1.0, 0.1, 0.55, 1), 1.4),
        "text_violet": material("REF_Text_Violet", (0.78, 0.52, 1.0, 1), 1, (0.6, 0.26, 1, 1), 1.0),
        "text_violet_dim": material("REF_Text_Violet_Dim", (0.5, 0.32, 0.72, 0.75), 0.75, (0.36, 0.16, 0.68, 1), 0.35),
        "ui_glass": material("REF_UI_Glass", (0.01, 0.03, 0.04, 0.62), 0.62, (0.02, 0.14, 0.12, 1), 0.2),
        "ask_glass": material("REF_Ask_Glass", (0.16, 0.06, 0.24, 0.38), 0.38, (0.36, 0.12, 0.62, 1), 0.34),
        "lime_glow": material("REF_Lime_Glow", (0.55, 1, 0.52, 0.42), 0.42, (0.48, 1, 0.36, 1), 2.4),
        "dot_cyan": material("REF_Dot_Cyan", (0.05, 0.9, 1, 0.88), 0.88, (0.0, 0.72, 1, 1), 1.2),
        "dot_violet": material("REF_Dot_Violet", (0.75, 0.28, 1, 0.86), 0.86, (0.62, 0.18, 1, 1), 1.15),
        "dot_green": material("REF_Dot_Green", (0.12, 0.9, 0.44, 0.82), 0.82, (0.04, 0.68, 0.22, 1), 0.9),
        "dot_pink": material("REF_Dot_Pink", (1, 0.28, 0.6, 0.8), 0.8, (0.9, 0.1, 0.34, 1), 0.9),
        "dot_warm": material("REF_Dot_Warm", (1, 0.75, 0.45, 0.72), 0.72, (0.7, 0.35, 0.12, 1), 0.62),
        "grain_dark": material("REF_Grain_Dark", (0.0, 0.0, 0.0, 0.10), 0.10),
        "grain_light": material("REF_Grain_Light", (0.8, 0.92, 0.95, 0.035), 0.035),
        "grain_violet": material("REF_Grain_Violet", (0.4, 0.18, 0.75, 0.045), 0.045),
    }

    existing_refs = [path for path in REFERENCE_IMAGES if path.exists()]
    if existing_refs:
        add_reference_image_card(1, existing_refs[1 % len(existing_refs)], (0.05, 1.08, -6.10), (3.25, 1.74, 0.08), col, mats)
        add_reference_image_card(2, existing_refs[2 % len(existing_refs)], (-4.10, 1.18, -6.24), (2.48, 1.72, 0.08), col, mats)
        add_reference_image_card(3, existing_refs[3 % len(existing_refs)], (3.78, 0.12, -6.03), (2.48, 1.46, 0.08), col, mats)
        add_reference_image_card(4, existing_refs[4 % len(existing_refs)], (0.95, -2.50, -6.38), (2.04, 1.08, 0.07), col, mats)
    else:
        add_reference_card(1, "SUSTAINABLE\nHORIZONS", (0.0, 1.02, -6.15), (3.18, 1.66, 0.08), mats["glass_center"], 0.39, col, mats)
        add_reference_card(2, "E.C.H.O.", (-4.05, 1.35, -6.28), (2.52, 1.80, 0.08), mats["glass_left"], 0.42, col, mats, align="LEFT")
        add_reference_card(3, "MISSION\nCONTROL", (3.72, 0.18, -6.05), (2.54, 1.48, 0.08), mats["glass_right"], 0.30, col, mats)
        add_reference_card(4, "DISCOVER\nYOUR\nPATRONUS", (1.10, -2.52, -6.42), (2.0, 1.05, 0.07), mats["glass_right"], 0.22, col, mats)

    add_organic_spine(col, mats)
    add_particle_clouds(col, mats)
    add_reference_ui(col, mats)
    add_film_grain(col, mats)
    revise_camera_and_render()


if __name__ == "__main__":
    main()
