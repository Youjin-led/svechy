import math
import random
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)
ASSET_PATH = Path(
    r"C:\Users\Ардор\OneDrive\Рабочий стол\3д художник\blender-mcp-work\assets\anatomy\nih_3d_3dpx_000307\First_lumbar_vertebra_NIH3D.glb"
)

random.seed(42)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def make_mat(
    name: str,
    color: tuple[float, float, float, float],
    metallic: float = 0.0,
    roughness: float = 0.35,
    emission=None,
    alpha: float | None = None,
):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    if alpha is not None and alpha < 1:
        mat.blend_method = "BLEND"
        mat.show_transparent_back = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if alpha is not None and "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if emission:
            bsdf.inputs["Emission Color"].default_value = emission[0]
            bsdf.inputs["Emission Strength"].default_value = emission[1]
    return mat


def make_image_mat(name: str, image_path: Path, alpha: float = 0.92):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    mat.show_transparent_back = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    image_node = nodes.new(type="ShaderNodeTexImage")
    image_node.image = bpy.data.images.load(str(image_path))
    if bsdf:
        mat.node_tree.links.new(image_node.outputs["Color"], bsdf.inputs["Base Color"])
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.04
        bsdf.inputs["Roughness"].default_value = 0.62
    return mat


def mesh_bounds(objects):
    points = []
    for obj in objects:
        if obj.type == "MESH":
            points.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not points:
        raise RuntimeError("Imported vertebra asset has no mesh geometry.")
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return lo, hi, hi - lo


def center_meshes(objects):
    lo, hi, _ = mesh_bounds(objects)
    center = (lo + hi) * 0.5
    for obj in objects:
        obj.location -= center


def import_nih_vertebra_source():
    if not ASSET_PATH.exists():
        raise FileNotFoundError(f"NIH vertebra asset not found: {ASSET_PATH}")
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ASSET_PATH))
    imported = [obj for obj in bpy.data.objects if obj not in before and obj.type == "MESH"]
    center_meshes(imported)
    _, _, dim = mesh_bounds(imported)
    scale = 2.65 / max(dim.x, dim.y, dim.z)
    for obj in imported:
        obj.scale = (scale, scale, scale)
        obj.rotation_euler.rotate_axis("X", math.radians(88))
        obj.rotation_euler.rotate_axis("Y", math.radians(-10))
        obj.rotation_euler.rotate_axis("Z", math.radians(-20))
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        obj.select_set(False)
    center_meshes(imported)
    return imported


def duplicate_vertebra_group(source_objects, name, loc, rot, scale, material):
    empty = bpy.data.objects.new(name, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.location = loc
    empty.rotation_euler = rot
    empty.scale = scale
    bpy.context.scene.collection.objects.link(empty)

    copies = []
    for src in source_objects:
        obj = src.copy()
        obj.data = src.data
        obj.name = f"{name}_{src.name[:24]}"
        obj.parent = empty
        obj.hide_viewport = False
        obj.hide_render = False
        obj.data.materials.clear()
        obj.data.materials.append(material)
        obj.modifiers.new("wet_anatomical_normals", "WEIGHTED_NORMAL")
        bpy.context.scene.collection.objects.link(obj)
        copies.append(obj)
    return empty, copies


def add_uv_ellipsoid(name: str, location, scale, material, segments=48, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    for vertex in obj.data.vertices:
        worldish = vertex.co
        ripple = 1.0 + 0.10 * math.sin(worldish.z * 7.0 + location[2]) + random.uniform(-0.035, 0.035)
        vertex.co.x *= ripple
        vertex.co.y *= 1.0 + random.uniform(-0.04, 0.04)
    bpy.ops.object.shade_smooth()
    return obj


def add_beveled_block(name: str, location, scale, rotation, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bevel = obj.modifiers.new(f"{name}_soft_chipped_edges", "BEVEL")
    bevel.width = 0.23
    bevel.segments = 14
    bevel.affect = "EDGES"
    obj.modifiers.new(f"{name}_weighted_normals", "WEIGHTED_NORMAL")
    texture = bpy.data.textures.new(f"{name}_surface_noise", "VORONOI")
    texture.noise_scale = 1.15
    texture.intensity = 0.23
    displace = obj.modifiers.new(f"{name}_subtle_lumpy_surface", "DISPLACE")
    displace.strength = 0.055
    displace.texture = texture
    bpy.ops.object.shade_smooth()
    return obj


def add_fin(name: str, location, rotation, scale, material):
    bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=0.45, radius2=0.05, depth=1.6, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj


def add_flat_process(name: str, location, rotation, scale, material):
    obj = add_uv_ellipsoid(name, location, scale, material, segments=32, rings=12)
    obj.rotation_euler = rotation
    return obj


def add_particle(name: str, location, radius, material):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    return obj


def add_constellation_line(name: str, start, end, material, thickness=0.006):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 2
    curve.bevel_depth = thickness
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    spline.points[0].co = (start[0], start[1], start[2], 1.0)
    spline.points[1].co = (end[0], end[1], end[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    obj.data.materials.append(material)
    bpy.context.scene.collection.objects.link(obj)
    if hasattr(obj, "visible_shadow"):
        obj.visible_shadow = False
    return obj


def add_text(name: str, text: str, location, size: float, material, align="LEFT"):
    bpy.ops.object.text_add(location=location, rotation=(math.radians(74), 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.004
    obj.data.materials.append(material)
    return obj


def rounded_rectangle_mesh(name: str, width: float, height: float, radius: float, location, material, segments=12):
    verts = []
    corners = [
        (width / 2 - radius, height / 2 - radius, 0.0),
        (-width / 2 + radius, height / 2 - radius, math.pi / 2),
        (-width / 2 + radius, -height / 2 + radius, math.pi),
        (width / 2 - radius, -height / 2 + radius, math.pi * 1.5),
    ]
    for cx, cz, start in corners:
        for step in range(segments + 1):
            angle = start + step * (math.pi / 2) / segments
            verts.append((cx + math.cos(angle) * radius, 0.0, cz + math.sin(angle) * radius))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [tuple(range(len(verts)))])
    mesh.update()
    uv_layer = mesh.uv_layers.new(name="CardUV")
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            vertex = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv_layer.data[loop_index].uv = ((vertex.x / width) + 0.5, (vertex.z / height) + 0.5)
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.data.materials.append(material)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def add_card_text(name: str, text: str, location, size: float, material, align="CENTER"):
    bpy.ops.object.text_add(location=location, rotation=(math.radians(90), 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = align
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.extrude = 0.006
    obj.data.materials.append(material)
    return obj


def add_project_card(name: str, center, width: float, height: float, angle: float, image_material, edge_material):
    card = rounded_rectangle_mesh(f"{name}_image", width, height, 0.18, center, image_material)
    card.rotation_euler = (0, 0, angle)

    edge = rounded_rectangle_mesh(
        f"{name}_edge",
        width + 0.055,
        height + 0.055,
        0.205,
        (center[0], center[1] - 0.010, center[2]),
        edge_material,
    )
    edge.rotation_euler = card.rotation_euler
    wire = edge.modifiers.new(f"{name}_thin_edge_wire", "WIREFRAME")
    wire.thickness = 0.012
    wire.use_even_offset = True
    return card, edge


clear_scene()

black = make_mat("deep_black_background", (0.0004, 0.003, 0.0035, 1), roughness=0.78)
metal = make_mat(
    "wet_iridescent_black_metal",
    (0.105, 0.095, 0.125, 1),
    metallic=0.86,
    roughness=0.13,
    emission=((0.018, 0.025, 0.050, 1), 0.16),
)
cyan = make_mat("dust_reference_cyan", (0.0, 0.55, 0.78, 1), roughness=0.28, emission=((0.0, 0.62, 0.95, 1), 1.55))
magenta = make_mat("dust_reference_magenta", (0.72, 0.12, 0.60, 1), roughness=0.30, emission=((0.85, 0.10, 0.72, 1), 1.30))
green = make_mat("dust_reference_green", (0.0, 0.72, 0.28, 1), roughness=0.28, emission=((0.0, 0.78, 0.30, 1), 1.18))
blue = make_mat("dust_reference_blue", (0.04, 0.18, 0.68, 1), roughness=0.30, emission=((0.05, 0.26, 0.88, 1), 1.25))
star_white = make_mat("milky_way_star_white", (0.78, 0.92, 1.0, 1), roughness=0.22, emission=((0.66, 0.86, 1.0, 1), 1.85))
star_violet = make_mat("milky_way_star_violet", (0.48, 0.22, 0.96, 1), roughness=0.25, emission=((0.62, 0.22, 1.0, 1), 1.65))
star_gold = make_mat("milky_way_star_warm_gold", (0.98, 0.64, 0.30, 1), roughness=0.25, emission=((1.0, 0.50, 0.12, 1), 1.30))
constellation_line = make_mat(
    "thin_constellation_blue_lines",
    (0.25, 0.72, 0.94, 0.32),
    roughness=0.35,
    emission=((0.10, 0.48, 0.82, 1), 0.55),
    alpha=0.32,
)
white_ui = make_mat("dim_white_ui", (0.72, 0.82, 0.90, 1), roughness=0.4, emission=((0.48, 0.62, 0.76, 1), 0.38))
card_glass = make_mat(
    "reference_card_smoked_teal_glass",
    (0.070, 0.145, 0.150, 0.66),
    metallic=0.12,
    roughness=0.72,
    emission=((0.003, 0.030, 0.030, 1), 0.045),
    alpha=0.66,
)
card_edge = make_mat(
    "reference_card_thin_cyan_edge",
    (0.16, 0.58, 0.54, 0.62),
    metallic=0.18,
    roughness=0.18,
    emission=((0.03, 0.36, 0.34, 1), 0.42),
    alpha=0.62,
)
card_wash = make_mat(
    "reference_card_muted_inner_wash",
    (0.20, 0.42, 0.38, 0.13),
    metallic=0.0,
    roughness=0.90,
    emission=((0.020, 0.12, 0.11, 1), 0.045),
    alpha=0.13,
)
card_warm_wash = make_mat(
    "reference_card_smoky_magenta_wash",
    (0.36, 0.13, 0.22, 0.10),
    metallic=0.0,
    roughness=0.88,
    emission=((0.10, 0.018, 0.055, 1), 0.035),
    alpha=0.10,
)
card_text = make_mat(
    "reference_card_soft_white_text",
    (0.82, 0.90, 0.94, 1),
    roughness=0.25,
    emission=((0.55, 0.74, 0.92, 1), 0.72),
)
card_image = make_image_mat(
    "reference_card_sustainable_horizons_texture",
    ROOT / "assets" / "reference_card_sustainable_horizons.png",
    alpha=0.91,
)

particle_mats = [cyan, cyan, blue, blue, magenta, green]
star_mats = [star_white, star_white, cyan, blue, star_violet, magenta, green, star_gold]

# Central spine: import one real NIH3D lumbar vertebra and duplicate it,
# matching the older workflow that produced the more anatomical result.
source_vertebra = import_nih_vertebra_source()
for obj in source_vertebra:
    obj.name = f"hidden_nih_source_{obj.name}"
    obj.hide_viewport = True
    obj.hide_render = True

spine_centers = []
vertebra_count = 22
for index in range(vertebra_count):
    t = index / (vertebra_count - 1)
    z = 7.45 - index * 0.72
    x = math.sin(t * math.pi * 1.18 - 0.38) * 0.15
    y = math.cos(t * math.pi * 0.92) * 0.055
    rotation = (
        math.radians(random.uniform(-3.0, 3.0)),
        math.radians(random.uniform(-4.0, 4.0)),
        math.radians(-18 + index * 2.2 + random.uniform(-1.2, 1.2)),
    )
    scale = 0.94 + math.sin(t * math.pi) * 0.12 + random.uniform(-0.018, 0.018)
    duplicate_vertebra_group(source_vertebra, f"real_nih_lumbar_vertebra_{index:02d}", (x, y, z), rotation, (scale, scale, scale), metal)
    spine_centers.append(Vector((x, y, z)))

# Procedural fallback kept dormant for quick iteration if the external anatomical asset is unavailable.
vertebrae = []
for index in range(0):
    z = -3.85 + index * 0.78
    twist = 0.16 * math.sin(index * 0.9)
    x = 0.13 * math.sin(index * 0.72)
    y = 0.06 * math.cos(index * 0.91)
    width = 0.92 + 0.10 * math.sin(index * 0.8)
    height = 0.34 + 0.04 * math.cos(index)
    depth = 0.42
    body = add_beveled_block(
        f"vertebra_{index:02d}",
        (x, y, z),
        (width, depth, height),
        (0.03 * math.sin(index), 0.12 * math.cos(index * 0.7), twist),
        metal,
    )
    vertebrae.append(body)

    front_bulge = add_uv_ellipsoid(
        f"front_body_bulge_{index:02d}",
        (x + 0.04 * math.sin(index * 1.3), y - 0.46, z + 0.01),
        (0.55 + 0.05 * random.random(), 0.12, 0.21 + 0.03 * random.random()),
        metal,
        segments=48,
        rings=18,
    )
    front_bulge.rotation_euler = (0.02 * math.sin(index), 0.04 * math.cos(index), twist)

    for lip_side, lip_z in [("top", z + height * 0.72), ("bottom", z - height * 0.74)]:
        add_flat_process(
            f"{lip_side}_rounded_lip_{index:02d}",
            (x - 0.02, y - 0.47, lip_z),
            (0.0, 0.0, twist + 0.06 * math.sin(index)),
            (0.67 + 0.05 * random.random(), 0.06, 0.045),
            metal,
        )

    # Front dark notch and wet highlight lip, so every segment reads like a vertebra.
    recess = add_uv_ellipsoid(
        f"front_recess_{index:02d}",
        (x + 0.10 * math.sin(index), y - 0.58, z + 0.015),
        (0.22 + 0.02 * random.random(), 0.028, 0.070),
        black,
        segments=32,
        rings=10,
    )
    recess.rotation_euler = (0.0, 0.0, twist)
    lip = add_flat_process(
        f"front_lower_lip_{index:02d}",
        (x - 0.03, y - 0.56, z - height * 0.55),
        (0.0, 0.0, twist),
        (0.38, 0.035, 0.045),
        metal,
    )

    for side in [-1, 1]:
        fin_angle = twist + side * math.radians(4)
        fin_location = (
            x + side * (0.70 + 0.07 * random.random()),
            y - 0.08 + 0.05 * random.random(),
            z + 0.02 + random.uniform(-0.05, 0.06),
        )
        add_flat_process(
            f"transverse_process_{index:02d}_{side}",
            fin_location,
            (0.0, 0.16 * side, fin_angle),
            (0.30 + random.random() * 0.12, 0.10, 0.075),
            metal,
        )
        add_fin(
            f"hook_process_{index:02d}_{side}",
            (
                x + side * (0.56 + 0.06 * random.random()),
                y - 0.34,
                z - height * 0.72,
            ),
            (math.radians(96 + random.uniform(-10, 8)), 0.08 * side, twist + side * 0.35),
            (0.23 + random.random() * 0.10, 0.08, 0.13),
            metal,
        )

    if index % 2 == 0:
        add_fin(
            f"rear_spike_{index:02d}",
            (x, y - 0.62, z + 0.03),
            (math.radians(88), 0, twist),
            (0.28, 0.10, 0.18),
            metal,
        )

# Reflective color freckles on the spine.
for index in range(360):
    z = random.uniform(-7.4, 7.4)
    angle = random.uniform(0, math.tau)
    radius = random.uniform(0.36, 0.74)
    mat = random.choice(particle_mats)
    add_particle(
        f"wet_color_speck_{index:03d}",
        (math.cos(angle) * radius * 0.75, math.sin(angle) * radius * 0.32, z),
        random.uniform(0.006, 0.018),
        mat,
    )

# Neon particle clouds, denser around the left and lower right like the reference.
for index in range(1900):
    cluster = random.random()
    if cluster < 0.48:
        center = Vector((-1.35, -0.05, 0.7))
        spread = Vector((1.55, 0.42, 5.9))
    elif cluster < 0.78:
        center = Vector((1.15, 0.05, -4.15))
        spread = Vector((1.80, 0.48, 2.2))
    else:
        center = Vector((0.3, 0.0, 4.2))
        spread = Vector((2.2, 0.5, 3.3))
    loc = Vector(
        (
            random.gauss(center.x, spread.x),
            random.gauss(center.y, spread.y),
            random.gauss(center.z, spread.z),
        )
    )
    if abs(loc.x) < 0.38 and random.random() < 0.35:
        loc.x += random.choice([-1, 1]) * random.uniform(0.35, 0.9)
    radius = random.triangular(0.0028, 0.020, 0.0065)
    add_particle(f"neon_dust_{index:04d}", loc, radius, random.choice(particle_mats))

# Deep matte environment shell. This replaces the old flat backdrop plane so
# the camera can orbit 360 degrees around the spine without crossing a wall.
bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=18.0, location=(0, 0, 0))
world_shell = bpy.context.object
world_shell.name = "deep_black_world_shell"
world_shell.data.materials.append(black)
bpy.ops.object.shade_smooth()
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=True)
bpy.ops.object.mode_set(mode="OBJECT")
if hasattr(world_shell, "visible_shadow"):
    world_shell.visible_shadow = False

# 360-degree star dust and constellation layer. The points live inside the
# environment shell, so the cosmic background still works when the camera orbits.
for index in range(280):
    theta = random.uniform(0, math.tau)
    z = random.uniform(-8.0, 8.0)
    radius = random.uniform(8.8, 16.2)
    wobble = 0.55 * math.sin(theta * 3.0 + z * 0.27)
    loc = (
        math.cos(theta) * (radius + wobble),
        math.sin(theta) * (radius + wobble),
        z + random.gauss(0, 0.22),
    )
    size = random.triangular(0.004, 0.024, 0.007)
    add_particle(f"deep_space_star_{index:03d}", loc, size, random.choice(star_mats))

for band in range(5):
    band_angle = band * math.tau / 8.0 + random.uniform(-0.18, 0.18)
    band_twist = random.choice([-1, 1]) * random.uniform(0.42, 0.68)
    z_start = random.uniform(-7.5, -4.2)
    z_span = random.uniform(8.8, 12.5)
    for step in range(72):
        t = step / 71
        theta = band_angle + band_twist * (t - 0.5) + random.gauss(0, 0.030)
        radius = random.gauss(7.7 + 2.0 * math.sin(t * math.pi), 0.58)
        z = z_start + z_span * t + math.sin(t * math.tau + band) * 0.65 + random.gauss(0, 0.34)
        loc = (
            math.cos(theta) * radius + random.gauss(0, 0.24),
            math.sin(theta) * radius + random.gauss(0, 0.24),
            z,
        )
        if random.random() < 0.30:
            mat = random.choice([magenta, star_violet, star_gold])
        elif random.random() < 0.68:
            mat = random.choice([cyan, blue, star_white])
        else:
            mat = random.choice([green, cyan])
        add_particle(f"milky_way_ribbon_{band:02d}_{step:03d}", loc, random.triangular(0.006, 0.045, 0.014), mat)

for cluster in range(8):
    theta = cluster * math.tau / 8.0 + random.uniform(-0.16, 0.16)
    radius = random.uniform(9.5, 13.8)
    center_z = random.uniform(-6.2, 6.4)
    tangent = Vector((-math.sin(theta), math.cos(theta), 0.0))
    vertical = Vector((0.0, 0.0, 1.0))
    center = Vector((math.cos(theta) * radius, math.sin(theta) * radius, center_z))
    points = []
    point_count = random.randint(4, 7)
    for point in range(point_count):
        offset = tangent * random.uniform(-0.65, 0.65) + vertical * random.uniform(-0.82, 0.82)
        loc = center + offset
        points.append(loc)
        add_particle(f"constellation_star_{cluster:02d}_{point:02d}", loc, random.uniform(0.025, 0.052), random.choice([star_white, cyan, star_gold]))
    for point in range(point_count - 1):
        add_constellation_line(
            f"constellation_line_{cluster:02d}_{point:02d}",
            points[point],
            points[point + 1],
            constellation_line,
            thickness=random.uniform(0.0035, 0.0065),
        )

# Fifteen cards: a real orbiting helix around the elongated spine.
# Each panel is yawed around the spine instead of being bill-boarded to camera,
# so foreground cards, side cards, and back cards read like the references.
card_count = 15
spiral_radius = 3.05
top_z = 6.70
bottom_z = -6.70
angle_step = math.tau / 5.0
start_angle = math.radians(246)
for index in range(card_count):
    t = index / (card_count - 1)
    angle = start_angle + index * angle_step
    x = math.cos(angle) * spiral_radius
    y = math.sin(angle) * spiral_radius * 0.95 - 0.34
    z = top_z + (bottom_z - top_z) * t
    depth_to_camera = max(0.0, (-y - 0.2) / (spiral_radius * 0.95))
    width = 3.35 + depth_to_camera * 1.45
    height = width * 0.60
    orbit_yaw = angle + math.pi / 2
    add_project_card(
        f"spiral_project_card_{index:02d}",
        (x, y, z),
        width,
        height,
        orbit_yaw,
        card_image,
        card_edge,
    )

# Minimal UI hints as spatial text, matching the reference without turning the scene into a flat page.
add_text("ui_prompt", "WHAT ARE YOU LOOKING FOR?", (-4.85, -1.45, -3.25), 0.13, white_ui)
for i, label in enumerate(["-> WEBSITES", "-> INSTALLATIONS", "-> XR / VR / AI", "-> MULTIPLAYER", "-> GAMES"]):
    add_text(f"ui_option_{i}", label, (-4.85, -1.45, -3.55 - i * 0.28), 0.12, magenta)
add_text("ui_top", "WORK        CONTACT", (2.95, -1.25, 4.35), 0.13, white_ui, align="CENTER")

# Camera and lighting.
bpy.ops.object.light_add(type="AREA", location=(-2.7, -2.8, 3.9))
key = bpy.context.object
key.name = "large_cyan_softbox"
key.data.energy = 1180
key.data.size = 4.8
key.data.color = (0.06, 0.62, 1.0)

bpy.ops.object.light_add(type="POINT", location=(1.8, -1.9, -2.1))
rim = bpy.context.object
rim.name = "lower_green_rim"
rim.data.energy = 760
rim.data.color = (0.02, 0.92, 0.36)

bpy.ops.object.light_add(type="POINT", location=(-1.25, -1.65, 2.2))
purple = bpy.context.object
purple.name = "magenta_spine_kicker"
purple.data.energy = 520
purple.data.color = (0.95, 0.12, 0.72)

bpy.ops.object.light_add(type="POINT", location=(0.35, -1.45, 3.2))
blue_glint = bpy.context.object
blue_glint.name = "small_blue_metal_glint"
blue_glint.data.energy = 340
blue_glint.data.color = (0.18, 0.52, 1.0)

bpy.ops.object.light_add(type="AREA", location=(0.25, -3.1, 0.25))
front_wash = bpy.context.object
front_wash.name = "soft_front_oil_slick_wash"
front_wash.data.energy = 420
front_wash.data.size = 5.6
front_wash.data.color = (0.42, 0.72, 1.0)

bpy.ops.object.light_add(type="POINT", location=(-0.85, -1.7, 0.65))
pink_glints = bpy.context.object
pink_glints.name = "small_pink_surface_glints"
pink_glints.data.energy = 300
pink_glints.data.color = (1.0, 0.20, 0.68)

bpy.ops.object.camera_add(location=(0.0, -11.2, 0.0), rotation=(math.radians(89), 0, 0))
camera = bpy.context.object
bpy.context.scene.camera = camera
camera.data.type = "ORTHO"
camera.data.ortho_scale = 17.5

orbit_rig = bpy.data.objects.new("camera_360_orbit_rig_rotate_z", None)
orbit_rig.empty_display_type = "CIRCLE"
orbit_rig.empty_display_size = 1.2
bpy.context.scene.collection.objects.link(orbit_rig)
camera.parent = orbit_rig
camera.matrix_parent_inverse = orbit_rig.matrix_world.inverted()

world = bpy.context.scene.world or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.color = (0.0005, 0.0035, 0.0045)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
if hasattr(scene, "eevee"):
    scene.eevee.taa_render_samples = 64
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.view_settings.view_transform = "Filmic"
scene.view_settings.look = "High Contrast"
scene.view_settings.exposure = -0.48
scene.view_settings.gamma = 1.0

# Save and export.
blend_path = OUTPUT / "scene.blend"
glb_path = OUTPUT / "scene.glb"
preview_path = OUTPUT / "preview.png"

bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB")
scene.render.filepath = str(preview_path)
bpy.ops.render.render(write_still=True)

print(f"[OK] blend={blend_path}")
print(f"[OK] glb={glb_path}")
print(f"[OK] preview={preview_path}")
