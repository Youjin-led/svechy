import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "attempts" / "reference_led_jellyfish_v13"
OUT.mkdir(parents=True, exist_ok=True)

FPS = 24
CYCLE = 96


def clean_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def set_socket(bsdf, names, value):
    for name in names:
        socket = bsdf.inputs.get(name)
        if socket:
            socket.default_value = value
            return


def make_material(name, color, alpha, emission, strength, roughness=0.42):
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
        set_socket(bsdf, ("Transmission Weight", "Transmission"), 0.18)
        set_socket(bsdf, ("Emission Color", "Emission"), emission)
        set_socket(bsdf, ("Emission Strength",), strength)
    mat.diffuse_color = color
    return mat


def make_bell(material):
    radial = 128
    rings = 30
    verts = []
    faces = []
    for r in range(rings + 1):
        v = r / rings
        dome = math.sin(v * math.pi * 0.5)
        base_radius = 1.03 * (dome ** 0.70)
        z = 0.82 * math.cos(v * math.pi * 0.5) - 0.20 * v
        for i in range(radial):
            theta = i / radial * math.tau
            scallop = math.sin(theta * 18.0 + math.sin(theta * 5.0) * 0.4)
            rim_weight = max(0.0, (v - 0.72) / 0.28) ** 1.8
            radius = base_radius * (1.0 + scallop * 0.030 * rim_weight)
            rim_drop = rim_weight * (0.050 + 0.020 * math.sin(theta * 18.0))
            verts.append((math.cos(theta) * radius, math.sin(theta) * radius, z - rim_drop))
    for r in range(rings):
        for i in range(radial):
            a = r * radial + i
            b = r * radial + (i + 1) % radial
            c = (r + 1) * radial + (i + 1) % radial
            d = (r + 1) * radial + i
            faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new("reference_jellyfish_bell_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("reference_jellyfish_bell", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)

    basis = obj.shape_key_add(name="Basis")
    contract = obj.shape_key_add(name="power_contract")
    rebound = obj.shape_key_add(name="elastic_rebound")
    for idx, vert in enumerate(mesh.vertices):
        co = vert.co
        radius = math.sqrt(co.x * co.x + co.y * co.y)
        v = max(0.0, min(1.0, (0.74 - co.z) / 0.92))
        rim = v ** 1.65
        crown = (1.0 - v) ** 2.0
        theta = math.atan2(co.y, co.x)
        fold = 1.0 + math.sin(theta * 16.0) * 0.035 * rim
        radial_contract = 1.0 - (0.12 + rim * 0.50) * fold
        contract.data[idx].co = Vector((
            co.x * radial_contract,
            co.y * radial_contract,
            co.z + rim * 0.30 - crown * 0.05,
        ))
        radial_rebound = 1.0 + rim * 0.045
        rebound.data[idx].co = Vector((
            co.x * radial_rebound,
            co.y * radial_rebound,
            co.z - rim * 0.035,
        ))

    animate_shape_key(mesh.shape_keys.key_blocks["power_contract"], [
        (1, 0.0), (10, 1.0), (22, 0.18), (34, 0.0), (70, 0.0), (CYCLE, 0.0)
    ])
    animate_shape_key(mesh.shape_keys.key_blocks["elastic_rebound"], [
        (1, 0.0), (10, 0.0), (22, 0.55), (34, 0.15), (48, 0.0), (CYCLE, 0.0)
    ])
    if mesh.shape_keys.animation_data and mesh.shape_keys.animation_data.action:
        mesh.shape_keys.animation_data.action.name = "jellyfish_bell_power_recoil"
    return obj


def animate_shape_key(shape_key, keys):
    for frame, value in keys:
        shape_key.value = value
        shape_key.keyframe_insert("value", frame=frame)


def make_tube_from_paths(name, paths, radius, sides, material):
    verts = []
    faces = []
    for path in paths:
        start = len(verts)
        for j, center in enumerate(path):
            tangent = (path[min(j + 1, len(path) - 1)] - path[max(j - 1, 0)])
            if tangent.length < 1e-5:
                tangent = Vector((0, 0, -1))
            tangent.normalize()
            normal = tangent.cross(Vector((0, 0, 1)))
            if normal.length < 1e-5:
                normal = Vector((1, 0, 0))
            normal.normalize()
            binormal = tangent.cross(normal)
            binormal.normalize()
            taper = 1.0 - (j / (len(path) - 1)) * 0.76
            for s in range(sides):
                a = s / sides * math.tau
                verts.append(tuple(center + (math.cos(a) * normal + math.sin(a) * binormal) * radius * taper))
        for j in range(len(path) - 1):
            for s in range(sides):
                a = start + j * sides + s
                b = start + j * sides + (s + 1) % sides
                c = start + (j + 1) * sides + (s + 1) % sides
                d = start + (j + 1) * sides + s
                faces.append((a, b, c, d))
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def make_ribbon_from_paths(name, paths, width, material):
    verts = []
    faces = []
    for path in paths:
        start = len(verts)
        for j, center in enumerate(path):
            tangent = (path[min(j + 1, len(path) - 1)] - path[max(j - 1, 0)])
            if tangent.length < 1e-5:
                tangent = Vector((0, 0, -1))
            tangent.normalize()
            side = tangent.cross(Vector((0, 1, 0)))
            if side.length < 1e-5:
                side = Vector((1, 0, 0))
            side.normalize()
            t = j / (len(path) - 1)
            ribbon_width = width * (1.0 - t * 0.55) * (0.78 + 0.22 * math.sin(t * math.tau * 2.0))
            verts.append(tuple(center - side * ribbon_width))
            verts.append(tuple(center + side * ribbon_width))
        for j in range(len(path) - 1):
            faces.append((start + j * 2, start + j * 2 + 1, start + (j + 1) * 2 + 1, start + (j + 1) * 2))
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def make_frilled_ribbon_from_paths(name, paths, width, material):
    verts = []
    faces = []
    strips = 7
    for path_i, path in enumerate(paths):
        start = len(verts)
        for j, center in enumerate(path):
            tangent = (path[min(j + 1, len(path) - 1)] - path[max(j - 1, 0)])
            if tangent.length < 1e-5:
                tangent = Vector((0, 0, -1))
            tangent.normalize()
            side = tangent.cross(Vector((0, 1, 0)))
            if side.length < 1e-5:
                side = Vector((1, 0, 0))
            side.normalize()
            t = j / (len(path) - 1)
            local_width = width * (1.0 - t * 0.46) * (0.90 + 0.14 * math.sin(t * math.tau * 1.6 + path_i))
            for s in range(strips):
                u = s / (strips - 1) * 2.0 - 1.0
                inner_wave = math.sin(t * math.tau * 2.0 + s * 0.65 + path_i * 0.8) * 0.012 * (1.0 - abs(u) * 0.45)
                edge_wave = math.sin(t * math.tau * 3.4 + path_i * 0.9) * 0.018 if s in (0, strips - 1) else 0.0
                verts.append(tuple(center + side * (u * local_width + inner_wave + edge_wave)))
        for j in range(len(path) - 1):
            for s in range(strips - 1):
                faces.append((
                    start + j * strips + s,
                    start + j * strips + s + 1,
                    start + (j + 1) * strips + s + 1,
                    start + (j + 1) * strips + s,
                ))
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def make_inner_glow(material):
    radial = 72
    rings = 10
    verts = []
    faces = []
    for r in range(rings + 1):
        t = r / rings
        radius = 0.10 + t * 0.42
        z = -0.14 - t * 0.24
        for i in range(radial):
            theta = i / radial * math.tau
            wobble = 1.0 + 0.08 * math.sin(theta * 7.0) * t
            verts.append((math.cos(theta) * radius * wobble, math.sin(theta) * radius * wobble, z))
    for r in range(rings):
        for i in range(radial):
            faces.append((r * radial + i, r * radial + (i + 1) % radial, (r + 1) * radial + (i + 1) % radial, (r + 1) * radial + i))
    mesh = bpy.data.meshes.new("reference_jellyfish_warm_inner_glow_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("reference_jellyfish_warm_inner_glow", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def make_oral_plume(material):
    rings = 34
    radial = 18
    verts = []
    faces = []
    base_paths = []
    for i in range(radial):
        theta = i / radial * math.tau
        base_paths.append([])
        for r in range(rings):
            t = r / (rings - 1)
            twist = theta + t * 1.15 + math.sin(t * math.tau * 1.8 + i) * 0.20
            radius = (0.20 + 0.22 * math.sin(t * math.pi * 1.15) ** 2) * (1.0 - t * 0.36)
            radius *= 1.0 + 0.16 * math.sin(i * 1.7 + t * math.tau * 3.2)
            z = -0.23 - 2.25 * (t ** 0.78)
            x = math.cos(twist) * radius + 0.06 * math.sin(t * math.tau * 0.8)
            y = math.sin(twist) * radius * 0.55
            base_paths[-1].append(Vector((x, y, z)))
            verts.append((x, y, z))
    for i in range(radial):
        ni = (i + 1) % radial
        for r in range(rings - 1):
            faces.append((i * rings + r, ni * rings + r, ni * rings + r + 1, i * rings + r + 1))
    mesh = bpy.data.meshes.new("reference_jellyfish_oral_plume_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("reference_jellyfish_oral_plume", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    for poly in obj.data.polygons:
        poly.use_smooth = True

    obj.shape_key_add(name="Basis")
    wave_a = obj.shape_key_add(name="soft_plume_wave_a")
    wave_b = obj.shape_key_add(name="soft_plume_wave_b")
    impulse = obj.shape_key_add(name="bell_impulse_tuck")
    for i in range(radial):
        for r in range(rings):
            idx = i * rings + r
            co = mesh.vertices[idx].co
            t = r / (rings - 1)
            amp = (0.04 + t * 0.18)
            phase = i * 0.62 + t * math.tau * 1.5
            wave_a.data[idx].co = Vector((co.x + math.sin(phase) * amp, co.y + math.cos(phase * 0.9) * amp * 0.22, co.z))
            wave_b.data[idx].co = Vector((co.x - math.sin(phase + 0.8) * amp * 0.75, co.y - math.cos(phase) * amp * 0.18, co.z - t * 0.05))
            impulse.data[idx].co = Vector((co.x * (1.0 - 0.25 * (1.0 - t)), co.y * (1.0 - 0.18 * (1.0 - t)), co.z + (1.0 - t) * 0.18))
    animate_shape_key(mesh.shape_keys.key_blocks["soft_plume_wave_a"], [
        (1, 0.10), (20, 0.75), (46, 0.30), (72, 0.88), (CYCLE, 0.10)
    ])
    animate_shape_key(mesh.shape_keys.key_blocks["soft_plume_wave_b"], [
        (1, 0.45), (24, 0.05), (52, 0.70), (CYCLE, 0.45)
    ])
    animate_shape_key(mesh.shape_keys.key_blocks["bell_impulse_tuck"], [
        (1, 0.0), (10, 0.70), (24, 0.18), (42, 0.0), (CYCLE, 0.0)
    ])
    if mesh.shape_keys.animation_data and mesh.shape_keys.animation_data.action:
        mesh.shape_keys.animation_data.action.name = "reference_jellyfish_oral_plume_water_follow"
    return obj


def build_oral_tail_paths(count, segments, radius, length, z0):
    paths = []
    for i in range(count):
        theta = -0.38 + i * 0.11
        root = Vector((math.cos(theta) * radius, math.sin(theta) * radius, z0))
        out = Vector((math.cos(theta), math.sin(theta), 0))
        tangent = Vector((-math.sin(theta), math.cos(theta), 0))
        path = []
        for j in range(segments):
            t = j / (segments - 1)
            p = (
                root
                + tangent * math.sin(t * math.tau * 0.55 + i * 0.9) * (0.025 + t * 0.16)
                + out * (0.012 + t * 0.10)
                + Vector((-0.10 * t, 0.0, -length * (t ** 0.78)))
            )
            path.append(p)
        paths.append(path)
    return paths


def make_rim_frill(material):
    count = 34
    seg = 8
    paths = []
    for i in range(count):
        theta = i / count * math.tau
        root = Vector((math.cos(theta) * 1.10, math.sin(theta) * 1.10, -0.20))
        tangent = Vector((-math.sin(theta), math.cos(theta), 0))
        out = Vector((math.cos(theta), math.sin(theta), 0))
        path = []
        for j in range(seg):
            t = j / (seg - 1)
            path.append(root + tangent * math.sin(t * math.pi * 1.8 + i * 0.35) * 0.012 + out * math.sin(t * math.pi + i) * 0.007 + Vector((0, 0, -0.045 * t)))
        paths.append(path)
    obj = make_tube_from_paths("reference_jellyfish_scalloped_rim_frill", paths, 0.006, 4, material)
    add_wave_keys(obj, paths, 4, 0.29, long=False)
    return obj


def make_bell_veins(material):
    paths = []
    count = 28
    for i in range(count):
        theta = i / count * math.tau
        path = []
        for j in range(18):
            v = 0.10 + j / 17 * 0.86
            dome = math.sin(v * math.pi * 0.5)
            radius = 1.11 * (dome ** 0.75) * (1.0 + 0.015 * math.sin(j * 0.9 + i))
            z = 0.70 * math.cos(v * math.pi * 0.5) - 0.20 * v - 0.010
            local_theta = theta + math.sin(v * math.pi * 1.7 + i * 0.3) * 0.018
            path.append(Vector((math.cos(local_theta) * radius, math.sin(local_theta) * radius, z)))
        paths.append(path)
    obj = make_tube_from_paths("reference_jellyfish_subtle_bell_veins", paths, 0.0045, 4, material)
    return obj


def add_wave_keys(obj, paths, sides, phase_step, long=False):
    mesh = obj.data
    obj.shape_key_add(name="Basis")
    wave_a = obj.shape_key_add(name="water_lag_a")
    wave_b = obj.shape_key_add(name="water_lag_b")
    impulse = obj.shape_key_add(name="impulse_follow")
    for path_i, path in enumerate(paths):
        phase = path_i * phase_step
        for j, _center in enumerate(path):
            t = j / (len(path) - 1)
            free = t ** (1.35 if long else 1.15)
            root_lock = max(0.0, min(1.0, (t - 0.06) / 0.94))
            amp = (0.12 + free * (0.42 if long else 0.22)) * root_lock
            down = (0.05 + free * (0.12 if long else 0.07)) * root_lock
            for s in range(sides):
                idx = (path_i * len(path) + j) * sides + s
                if idx >= len(mesh.vertices):
                    continue
                co = mesh.vertices[idx].co
                wave = math.sin(t * math.tau * 2.2 + phase)
                cross = math.cos(t * math.tau * 1.6 + phase)
                wave_a.data[idx].co = Vector((co.x + amp * wave, co.y + amp * 0.45 * cross, co.z - down * 0.30))
                wave_b.data[idx].co = Vector((co.x - amp * math.sin(t * math.tau * 2.0 + phase + 0.7), co.y - amp * 0.55 * cross, co.z - down * 0.65))
                impulse.data[idx].co = Vector((co.x + amp * 0.30 * wave, co.y + amp * 0.25 * cross, co.z + down * 0.95))

    animate_shape_key(mesh.shape_keys.key_blocks["impulse_follow"], [
        (1, 0.0), (12, 0.85), (24, 0.30), (38, 0.0), (CYCLE, 0.0)
    ])
    animate_shape_key(mesh.shape_keys.key_blocks["water_lag_a"], [
        (1, 0.0), (18, 0.25), (34, 0.95), (56, 0.24), (CYCLE, 0.0)
    ])
    animate_shape_key(mesh.shape_keys.key_blocks["water_lag_b"], [
        (1, 0.15), (20, 0.0), (48, 0.72), (72, 0.36), (CYCLE, 0.15)
    ])
    if mesh.shape_keys.animation_data and mesh.shape_keys.animation_data.action:
        mesh.shape_keys.animation_data.action.name = f"{obj.name}_water_follow"


def build_tentacle_paths(count, segments, radius, length, z0, long=False):
    paths = []
    for i in range(count):
        theta = i / count * math.tau
        # Keep the silhouette closer to the reference: not an even cylinder of strings,
        # but sparse, slightly grouped marginal tentacles around the visible rim.
        cluster = math.sin(i * 1.91) * 0.16 + math.sin(i * 0.71) * 0.08
        theta += cluster
        root = Vector((math.cos(theta) * radius, math.sin(theta) * radius, z0))
        out = Vector((math.cos(theta), math.sin(theta), 0))
        tangent = Vector((-math.sin(theta), math.cos(theta), 0))
        path = []
        for j in range(segments):
            t = j / (segments - 1)
            sway = (
                math.sin(t * math.pi * (0.92 if long else 0.80) + i * 0.73) * (0.035 + t * (0.34 if long else 0.16))
                + math.sin(t * math.pi * 2.6 + i * 0.31) * (0.010 + t * (0.09 if long else 0.05))
            )
            drift = (
                math.cos(t * math.pi * 0.82 + i * 0.43) * (0.014 + t * (0.18 if long else 0.07))
                + math.sin(t * math.pi * 2.2 + i * 0.19) * (0.004 + t * 0.055)
            )
            p = root + out * drift + tangent * sway + Vector((0, 0, -length * (t ** (1.02 if long else 0.92))))
            path.append(p)
        paths.append(path)
    return paths


def build_oral_ribbon_paths(count, segments, radius, length, z0):
    paths = []
    for i in range(count):
        u = i / max(1, count - 1) * 2.0 - 1.0
        root = Vector((u * radius * 2.05, math.sin(i * 1.7) * radius * 0.34, z0 - (i % 3) * 0.035))
        out = Vector((0.25 + u * 0.28, math.sin(i * 1.1) * 0.12, 0))
        tangent = Vector((0.55, 0.0, 0))
        path = []
        local_length = length * (0.48 + 0.24 * math.sin(i * 1.7) + 0.18 * (i % 2))
        for j in range(segments):
            t = j / (segments - 1)
            p = (
                root
                + tangent * math.sin(t * math.tau * (0.54 + (i % 2) * 0.16) + i * 0.82) * (0.030 + t * 0.16)
                + out * (math.cos(t * math.tau * 0.46 + i * 0.48) * (0.010 + t * 0.055) + t * 0.08)
                + Vector((0.02 * t, 0.0, -local_length * (t ** 0.66)))
            )
            path.append(p)
        paths.append(path)
    return paths


def add_root_animation(root):
    keys = [
        (1, (0, 0, 0), 1.0),
        (10, (0, 0, 0.20), 0.992),
        (26, (0, 0, 0.42), 1.0),
        (54, (0, 0, 0.24), 1.002),
        (CYCLE, (0, 0, 0), 1.0),
    ]
    for frame, loc, scale in keys:
        root.location = loc
        root.scale = (scale, scale, scale)
        root.keyframe_insert("location", frame=frame)
        root.keyframe_insert("scale", frame=frame)
    if root.animation_data and root.animation_data.action:
        root.animation_data.action.name = "jellyfish_root_swim_cycle"


def setup_scene():
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = CYCLE
    scene.render.fps = FPS
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 96
    scene.render.resolution_x = 768
    scene.render.resolution_y = 1024
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.film_transparent = False
    scene.world.color = (0.002, 0.006, 0.016)

    cam_data = bpy.data.cameras.new("jellyfish_candidate_camera")
    cam = bpy.data.objects.new("jellyfish_candidate_camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0, -8.8, -1.42)
    cam.rotation_euler = (math.radians(88), 0, 0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 5.65
    scene.camera = cam

    bg_data = bpy.data.meshes.new("reference_jellyfish_dark_water_backdrop_mesh")
    bg_data.from_pydata(
        [(-4.0, 2.8, -5.3), (4.0, 2.8, -5.3), (4.0, 2.8, 2.2), (-4.0, 2.8, 2.2)],
        [],
        [(0, 1, 2, 3)],
    )
    bg_data.update()
    bg = bpy.data.objects.new("reference_jellyfish_dark_water_backdrop", bg_data)
    bpy.context.collection.objects.link(bg)
    bg_mat = bpy.data.materials.new("reference_jellyfish_deep_ocean_emission")
    bg_mat.use_nodes = True
    nodes = bg_mat.node_tree.nodes
    nodes.clear()
    emission = nodes.new(type="ShaderNodeEmission")
    emission.inputs["Color"].default_value = (0.002, 0.008, 0.025, 1.0)
    emission.inputs["Strength"].default_value = 1.0
    output = nodes.new(type="ShaderNodeOutputMaterial")
    bg_mat.node_tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
    bg.data.materials.append(bg_mat)

    for name, loc, color, power in [
        ("cyan_key", (-2.4, -3.0, 2.3), (0.1, 0.9, 1.0), 260),
        ("magenta_rim", (2.3, -2.6, 1.1), (1.0, 0.15, 0.65), 300),
        ("soft_top", (0, 1.2, 3.8), (0.65, 0.75, 1.0), 120),
        ("warm_core", (0, -1.6, -0.35), (1.0, 0.28, 0.10), 210),
    ]:
        light_data = bpy.data.lights.new(name, "POINT")
        light_data.color = color
        light_data.energy = power
        light = bpy.data.objects.new(name, light_data)
        light.location = loc
        bpy.context.collection.objects.link(light)


def main():
    clean_scene()
    setup_scene()
    bell_mat = make_material("candidate_bell_rose_cyan_glass", (0.72, 0.74, 1.0, 0.30), 0.30, (0.22, 0.68, 1.0, 1), 0.42)
    vein_mat = make_material("candidate_bell_inner_rose_veins", (1.0, 0.45, 0.72, 0.24), 0.24, (1.0, 0.18, 0.46, 1), 0.34, 0.70)
    rim_mat = make_material("candidate_rim_coral_glow", (1.0, 0.30, 0.42, 0.62), 0.62, (1.0, 0.15, 0.34, 1), 0.82, 0.50)
    tentacle_mat = make_material("candidate_tentacle_rosy_biolume", (1.0, 0.22, 0.72, 0.34), 0.34, (1.0, 0.10, 0.62, 1), 0.52, 0.66)
    oral_mat = make_material("candidate_oral_arm_peach_glow", (1.0, 0.36, 0.24, 0.34), 0.34, (1.0, 0.20, 0.10, 1), 0.46, 0.62)
    tail_mat = make_material("candidate_oral_tail_rose_glow", (1.0, 0.18, 0.42, 0.30), 0.30, (1.0, 0.08, 0.36, 1), 0.42, 0.66)

    root = bpy.data.objects.new("reference_jellyfish_root", None)
    bpy.context.collection.objects.link(root)
    add_root_animation(root)

    bell = make_bell(bell_mat)
    bell.parent = root
    veins = make_bell_veins(vein_mat)
    veins.parent = root
    rim = make_rim_frill(rim_mat)
    rim.parent = root

    marginal_paths = build_tentacle_paths(22, 56, 0.96, 4.75, -0.27, long=True)
    marginal = make_tube_from_paths("reference_jellyfish_long_tentacles", marginal_paths, 0.0022, 4, tentacle_mat)
    marginal.parent = root
    add_wave_keys(marginal, marginal_paths, 4, 0.43, long=True)

    oral_paths = build_oral_ribbon_paths(13, 62, 0.18, 2.60, -0.22)
    oral = make_frilled_ribbon_from_paths("reference_jellyfish_oral_arms", oral_paths, 0.040, oral_mat)
    oral.parent = root
    add_wave_keys(oral, oral_paths, 7, 0.85, long=False)

    tail_paths = build_oral_tail_paths(3, 82, 0.08, 2.55, -1.42)
    tail = make_frilled_ribbon_from_paths("reference_jellyfish_trailing_oral_tail", tail_paths, 0.024, tail_mat)
    tail.parent = root
    add_wave_keys(tail, tail_paths, 7, 0.67, long=False)

    text = bpy.data.texts.new("REFERENCE_LED_JELLYFISH_NOTES")
    text.write("Motion references: fast bell contraction/power stroke, passive elastic recoil, interpulse drift; tentacles lag and continue water wave.\n")
    text.write("Created as a draft procedural Blender candidate before site integration.\n")

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "jellyfish_candidate.blend"))
    bpy.ops.export_scene.gltf(
        filepath=str(OUT / "jellyfish_candidate.glb"),
        export_format="GLB",
        export_animations=True,
        export_lights=True,
        export_cameras=True,
    )
    bpy.context.scene.frame_set(26)
    bpy.context.scene.render.filepath = str(OUT / "jellyfish_candidate_preview.png")
    bpy.ops.render.render(write_still=True)
    print("SAVED", OUT / "jellyfish_candidate.blend", OUT / "jellyfish_candidate.glb", OUT / "jellyfish_candidate_preview.png")


if __name__ == "__main__":
    main()
