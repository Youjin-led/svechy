import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(r"C:\Users\Ардор\OneDrive\Рабочий стол\JS\ДЗ-1")
OUT = ROOT / "3d_model_dlya_konstruktora"
OUT.mkdir(parents=True, exist_ok=True)

W = 2.13
H = 1.85
D = 0.235


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.images):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def collection(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def link_to(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)


def material(name, color, metallic=0.0, roughness=0.45, alpha=1.0, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Alpha"].default_value = alpha
    if emission:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = strength
    m.blend_method = "BLEND"
    m.use_screen_refraction = True
    return m


MAT_FRAME = None
MAT_INNER = None
MAT_MIRROR = None
MAT_FRONT = None
MAT_GOLD = None
MAT_CARD = None
MAT_RED = None
MAT_BLACK = None
MAT_TOKEN = None
MAT_LED = None
MAT_LABEL = None
MAT_LABEL_LIGHT = None


def make_materials():
    global MAT_FRAME, MAT_INNER, MAT_MIRROR, MAT_FRONT, MAT_GOLD, MAT_CARD
    global MAT_RED, MAT_BLACK, MAT_TOKEN, MAT_LED, MAT_LABEL, MAT_LABEL_LIGHT
    MAT_FRAME = material("01 matte black structural box / корпус", (0.02, 0.018, 0.015, 1), roughness=0.38)
    MAT_INNER = material("01 dark inner backing / внутренняя основА", (0.01, 0.012, 0.014, 1), roughness=0.55)
    MAT_MIRROR = material("02 blue mirror glass / зеркала", (0.22, 0.56, 0.85, 0.34), metallic=0.55, roughness=0.04, alpha=0.34)
    MAT_FRONT = material("02 transparent front one-way mirror / переднее зеркало", (0.55, 0.83, 1.0, 0.18), metallic=0.25, roughness=0.02, alpha=0.18)
    MAT_GOLD = material("gold paint / золото", (0.98, 0.62, 0.16, 1), metallic=0.2, roughness=0.28)
    MAT_CARD = material("04 painted MDF cards / карты MDF", (0.74, 0.47, 0.18, 1), roughness=0.48)
    MAT_RED = material("04 red painted MDF chips / красные фишки", (0.75, 0.04, 0.025, 1), roughness=0.34)
    MAT_BLACK = material("04 black-gold MDF chips / черные фишки", (0.025, 0.02, 0.018, 1), roughness=0.28)
    MAT_TOKEN = material("04 gold MDF tokens / жетоны", (0.95, 0.62, 0.18, 1), metallic=0.15, roughness=0.3)
    MAT_LED = material("03 warm LED glow / LED", (1.0, 0.55, 0.05, 1), emission=(1, 0.42, 0.02, 1), strength=1.1)
    MAT_LABEL = material("labels black", (0, 0, 0, 1), roughness=0.5)
    MAT_LABEL_LIGHT = material("labels light", (1.0, 0.92, 0.72, 1), roughness=0.5)


def cube(name, loc, scale, mat, col):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    link_to(obj, col)
    return obj


def cyl(name, loc, radius, depth, mat, col, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc, rotation=(math.pi / 2, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    link_to(obj, col)
    return obj


def bevel_object(obj, amount=0.01, segments=3):
    bevel = obj.modifiers.new("small bevels", "BEVEL")
    bevel.width = amount
    bevel.segments = segments
    bevel.affect = "EDGES"
    obj.modifiers.new("weighted normals", "WEIGHTED_NORMAL")


def text_obj(name, text, loc, size, col, mat=MAT_LABEL, rot=(math.radians(70), 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.materials.append(mat)
    link_to(obj, col)
    return obj


def add_curve_rect(name, x, z, w, h, y, col, mat, bevel=0.012):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel
    curve.resolution_u = 2
    points = [
        (-W / 2 + x, y, -H / 2 + z),
        (-W / 2 + x + w, y, -H / 2 + z),
        (-W / 2 + x + w, y, -H / 2 + z + h),
        (-W / 2 + x, y, -H / 2 + z + h),
        (-W / 2 + x, y, -H / 2 + z),
    ]
    poly = curve.splines.new("POLY")
    poly.points.add(len(points) - 1)
    for p, co in zip(poly.points, points):
        p.co = (co[0], co[1], co[2], 1)
    obj = bpy.data.objects.new(name, curve)
    obj.data.materials.append(mat)
    col.objects.link(obj)
    return obj


def add_card(name, cx_mm, cy_mm, rot_deg, rank, col):
    x = -W / 2 + cx_mm / 1000
    z = H / 2 - cy_mm / 1000
    obj = cube(name, (x, -0.055, z), (0.26, 0.008, 0.39), MAT_CARD, col)
    obj.rotation_euler[1] = math.radians(rot_deg)
    bevel_object(obj, 0.008, 4)
    text_obj("rank_" + name, rank, (x - 0.085, -0.063, z + 0.145), 0.055, col, MAT_LABEL_LIGHT, rot=(math.radians(90), 0, 0))
    text_obj("spade_" + name, "♠", (x, -0.064, z - 0.015), 0.13, col, MAT_LABEL, rot=(math.radians(90), 0, 0))
    return obj


def add_chip(name, cx_mm, cy_mm, mat, col):
    x = -W / 2 + cx_mm / 1000
    z = H / 2 - cy_mm / 1000
    obj = cyl(name, (x, -0.078, z), 0.0725, 0.012, mat, col)
    cyl(name + "_gold_ring", (x, -0.086, z), 0.048, 0.004, MAT_GOLD, col)
    cyl(name + "_center", (x, -0.091, z), 0.022, 0.004, MAT_TOKEN, col)
    for i in range(8):
        a = math.radians(i * 45)
        cyl(name + f"_dot_{i}", (x + math.cos(a) * 0.058, -0.094, z + math.sin(a) * 0.058), 0.0065, 0.003, MAT_GOLD, col, vertices=24)
    return obj


def add_token(name, cx_mm, cy_mm, col):
    x = -W / 2 + cx_mm / 1000
    z = H / 2 - cy_mm / 1000
    cyl(name, (x, -0.082, z), 0.0425, 0.009, MAT_TOKEN, col)
    cyl(name + "_inner", (x, -0.089, z), 0.024, 0.003, MAT_BLACK, col)


def build_model(exploded=False):
    clear_scene()
    make_materials()
    col_frame = collection("01_BOX_FRAME")
    col_mirror = collection("02_MIRRORS")
    col_led = collection("03_LED_ZONES")
    col_mdf = collection("04_MDF_OBJECTS")
    col_labels = collection("05_LABELS_AND_NOTES")

    explode = 0.0
    front_y = -D / 2
    led_y = -0.09
    mdf_y = -0.055
    back_y = D / 2
    if exploded:
        front_y = -0.55
        led_y = -0.25
        mdf_y = 0.03
        back_y = 0.36
        explode = 1.0

    # Structure: open front box + rear backing.
    back = cube("back structural panel 2130x1850", (0, back_y, 0), (W, 0.018, H), MAT_INNER, col_frame)
    left = cube("left structural side depth 235", (-W / 2 + 0.021, 0, 0), (0.042, D, H), MAT_FRAME, col_frame)
    right = cube("right structural side depth 235", (W / 2 - 0.021, 0, 0), (0.042, D, H), MAT_FRAME, col_frame)
    top = cube("top structural side depth 235", (0, 0, H / 2 - 0.021), (W, D, 0.042), MAT_FRAME, col_frame)
    bottom = cube("bottom structural side depth 235", (0, 0, -H / 2 + 0.021), (W, D, 0.042), MAT_FRAME, col_frame)
    for obj in (back, left, right, top, bottom):
        bevel_object(obj, 0.004, 2)

    cube("front transparent one-way mirror 2110x1830", (0, front_y, 0), (2.11, 0.006, 1.83), MAT_FRONT, col_mirror)
    cube("rear mirror 1950x1670", (0, back_y - 0.018, 0), (1.95, 0.006, 1.67), MAT_MIRROR, col_mirror)
    cube("left depth mirror 1670x235", (-0.975, 0.0 if not exploded else 0.18, 0), (0.006, D, 1.67), MAT_MIRROR, col_mirror)
    cube("right depth mirror 1670x235", (0.975, 0.0 if not exploded else 0.18, 0), (0.006, D, 1.67), MAT_MIRROR, col_mirror)
    cube("top depth mirror 1950x235", (0, 0.0 if not exploded else 0.18, 0.835), (1.95, D, 0.006), MAT_MIRROR, col_mirror)
    cube("bottom depth mirror 1950x235", (0, 0.0 if not exploded else 0.18, -0.835), (1.95, D, 0.006), MAT_MIRROR, col_mirror)

    add_curve_rect("LED A outer contour approx 7.6m", 0.045, 0.045, 2.04, 1.76, led_y, col_led, MAT_LED, 0.006)
    add_curve_rect("LED B inner contour approx 6.1m", 0.19, 0.17, 1.75, 1.51, led_y + 0.006, col_led, MAT_LED, 0.005)
    add_curve_rect("LED C central tunnel approx 4.5m", 0.455, 0.39, 1.22, 1.04, led_y + 0.012, col_led, MAT_LED, 0.005)

    # Cards: y values use image top-down coordinates from earlier tech project.
    cards = [
        ("card_10_spades MDF 260x390", 740, 360, -22, "10"),
        ("card_J1_spades MDF 260x390", 835, 330, -14, "J"),
        ("card_J2_spades MDF 260x390", 930, 305, -7, "J"),
        ("card_Q_spades MDF 260x390", 1030, 285, 0, "Q"),
        ("card_K_spades MDF 260x390", 1135, 300, 8, "K"),
        ("card_A_spades MDF 260x390", 1245, 335, 18, "A"),
    ]
    for name, cx, cy, rot, rank in cards:
        obj = add_card(name, cx, cy, rot, rank, col_mdf)
        obj.location.y = mdf_y

    chips = [
        ("C1 red chip D145", 350, 365, MAT_RED),
        ("C2 black-gold chip D145", 425, 650, MAT_BLACK),
        ("C3 red chip D145", 350, 980, MAT_RED),
        ("C4 black-gold chip D145", 365, 1350, MAT_BLACK),
        ("C5 black-gold chip D145", 1780, 365, MAT_BLACK),
        ("C6 red chip D145", 1705, 650, MAT_RED),
        ("C7 black-gold chip D145", 1780, 980, MAT_BLACK),
        ("C8 red chip D145", 1765, 1350, MAT_RED),
    ]
    for name, cx, cy, mat in chips:
        add_chip(name, cx, cy, mat, col_mdf)

    tokens = [
        ("T1 token D85", 360, 515), ("T2 token D85", 420, 810), ("T3 token D85", 370, 1165), ("T4 token D85", 300, 1510),
        ("T5 token D85", 1770, 515), ("T6 token D85", 1710, 810), ("T7 token D85", 1760, 1165), ("T8 token D85", 1830, 1510),
        ("T9 token D85", 620, 1280), ("T10 token D85", 1510, 1280), ("T11 token D85", 760, 575), ("T12 token D85", 1370, 575),
    ]
    for name, cx, cy in tokens:
        add_token(name, cx, cy, col_mdf)

    # Small suit placeholders around border.
    for i, (cx, cy, symbol) in enumerate([
        (280, 1600, "♣"), (520, 1600, "♠"), (840, 1600, "♦"), (1065, 1600, "♠"), (1290, 1600, "♥"), (1610, 1600, "♣"), (1850, 1600, "♠"),
        (300, 255, "♣"), (1830, 255, "♠"), (540, 250, "♦"), (1590, 250, "♥"),
    ]):
        x = -W / 2 + cx / 1000
        z = H / 2 - cy / 1000
        text_obj(f"suit_{i}_{symbol}", symbol, (x, -0.092, z), 0.055, col_mdf, MAT_GOLD, rot=(math.radians(90), 0, 0))

    # Explainer labels.
    text_obj("label_title", "Casino infinity mirror: 2130 x 1850 x 235 mm", (0, -0.72 if exploded else -0.23, 1.08), 0.075, col_labels, MAT_LABEL_LIGHT if not exploded else MAT_LABEL)
    if exploded:
        text_obj("label_front", "0 mm: front one-way mirror", (-0.72, front_y, 0.97), 0.045, col_labels)
        text_obj("label_led", "20-35 mm: warm LED contours", (-0.55, led_y, 0.78), 0.045, col_labels)
        text_obj("label_mdf", "55-125 mm: MDF cards / chips / tokens", (-0.35, mdf_y, 0.58), 0.045, col_labels)
        text_obj("label_back", "220-235 mm: rear mirror + structural back", (0.05, back_y, 0.38), 0.045, col_labels)
    else:
        text_obj("label_hide_front", "Tip: hide collection 02_MIRRORS to see inside", (0, -0.24, -1.05), 0.045, col_labels, MAT_LABEL_LIGHT)


def setup_camera(name, loc, target, ortho_scale):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    cam.name = name
    direction = Vector(target) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    return cam


def setup_lighting():
    bpy.ops.object.light_add(type="AREA", location=(0, -2.4, 2.4))
    light = bpy.context.object
    light.name = "large softbox"
    light.data.energy = 430
    light.data.size = 4.0
    bpy.ops.object.light_add(type="POINT", location=(0, -0.8, 0.2))
    p = bpy.context.object
    p.name = "warm internal glow"
    p.data.energy = 35
    p.data.color = (1, 0.58, 0.12)


def render(path, camera):
    bpy.context.scene.camera = camera
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.eevee.taa_render_samples = 32
    bpy.context.scene.render.resolution_x = 1700
    bpy.context.scene.render.resolution_y = 1200
    bpy.context.scene.view_settings.view_transform = "Standard"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.world.color = (0.06, 0.055, 0.05)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def set_front_mirror_hidden(hidden):
    obj = bpy.data.objects.get("front transparent one-way mirror 2110x1830")
    if obj:
        obj.hide_viewport = hidden
        obj.hide_render = hidden


def save_readme():
    (OUT / "README_3D_MODEL.txt").write_text(
        """3D model for constructor

Files:
- casino_mirror_constructor_model.blend: main Blender source.
- casino_mirror_constructor_model.glb: exchange model for viewers.
- preview_assembled_front.png: assembled front view.
- preview_assembled_iso.png: assembled isometric view.
- preview_exploded_layers.png: exploded layer explanation.

Collections inside Blender:
- 01_BOX_FRAME: structural box.
- 02_MIRRORS: front/rear/side mirrors. Hide this collection to see inside.
- 03_LED_ZONES: warm LED contours.
- 04_MDF_OBJECTS: cards, chips, tokens, suits.
- 05_LABELS_AND_NOTES: explanatory labels.

This is an explanatory model, not final engineering CAD. It shows composition, layers, and construction intent for a constructor.
""",
        encoding="utf-8",
    )


def main():
    build_model(exploded=False)
    setup_lighting()
    cam_front = setup_camera("Camera_front", (0, -3.1, 0.02), (0, 0, 0.02), 2.48)
    cam_iso = setup_camera("Camera_iso", (1.6, -2.8, 1.55), (0, 0, 0), 2.55)
    set_front_mirror_hidden(True)
    render(OUT / "preview_assembled_front.png", cam_front)
    render(OUT / "preview_assembled_iso.png", cam_iso)
    set_front_mirror_hidden(False)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "casino_mirror_constructor_model.blend"))
    bpy.ops.export_scene.gltf(filepath=str(OUT / "casino_mirror_constructor_model.glb"), export_format="GLB")

    build_model(exploded=True)
    setup_lighting()
    cam_exploded = setup_camera("Camera_exploded", (1.55, -3.1, 1.55), (0, 0.02, 0), 2.7)
    render(OUT / "preview_exploded_layers.png", cam_exploded)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "casino_mirror_constructor_model_exploded.blend"))
    save_readme()


if __name__ == "__main__":
    main()
