from pathlib import Path
import json
import math
import shutil

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
WORK_ASSET = Path(r"C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2\assets\baked_geonodes_jellyfish.glb")
OUT = ROOT / "output" / "attempts" / "realistic_baked_jellyfish_motion_v3"
OUT.mkdir(parents=True, exist_ok=True)


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def smoothstep(edge0, edge1, value):
    if edge0 == edge1:
        return 0.0
    x = clamp((value - edge0) / (edge1 - edge0))
    return x * x * (3.0 - 2.0 * x)


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def remove_shape_keys(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    while obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 1:
        obj.active_shape_key_index = len(obj.data.shape_keys.key_blocks) - 1
        bpy.ops.object.shape_key_remove()


def bounds_for_vertices(vertices):
    xs = [co.x for co in vertices]
    ys = [co.y for co in vertices]
    zs = [co.z for co in vertices]
    return {
        "x_min": min(xs),
        "x_max": max(xs),
        "y_min": min(ys),
        "y_max": max(ys),
        "z_min": min(zs),
        "z_max": max(zs),
        "r_max": max(math.hypot(co.x, co.y) for co in vertices),
    }


def deform_vertex(co, bounds, *, contraction, rebound, lag_phase, lag_amount, settle, tuck, stream):
    x, y, z = co.x, co.y, co.z
    radius = math.hypot(x, y)
    r_norm = radius / max(bounds["r_max"], 0.001)

    bell = smoothstep(0.05, 0.72, z)
    lower_bell = bell * (1.0 - smoothstep(1.05, 1.72, z) * 0.65)
    rim = lower_bell * smoothstep(0.34, 0.72, r_norm)
    crown = smoothstep(1.02, 1.72, z)
    tentacle = 1.0 - smoothstep(-0.18, 0.28, z)
    depth = clamp((0.24 - z) / (0.24 - bounds["z_min"]))
    tip = depth * depth
    oral = smoothstep(-0.72, 0.50, z) * (1.0 - smoothstep(0.42, 1.0, z))

    angle = math.atan2(y, x) if radius > 0.0001 else 0.0
    radial_scale = 1.0
    radial_scale -= contraction * (0.33 * rim + 0.12 * lower_bell)
    radial_scale += rebound * (0.13 * rim + 0.08 * lower_bell)
    radial_scale += settle * 0.045 * math.sin(angle * 4.0 + depth * 3.0) * tentacle
    radial_scale -= contraction * tentacle * (0.28 * depth + 0.10 * tip)
    radial_scale += tuck * tentacle * (0.12 + 0.26 * depth)
    radial_scale -= stream * tentacle * (0.14 + 0.20 * depth)

    nx = x * radial_scale
    ny = y * radial_scale

    # Fast bell pulse: the rim tucks upward/inward, the crown compresses a little,
    # then the elastic rebound opens the umbrella before the tentacles catch up.
    nz = z
    nz += contraction * (0.27 * rim - 0.08 * crown + 0.13 * oral)
    nz += rebound * (0.10 * crown - 0.10 * rim - 0.05 * oral)

    lag_wave = math.sin(depth * 9.0 + angle * 1.35 + lag_phase)
    cross_wave = math.cos(depth * 6.2 + angle * 2.1 + lag_phase * 0.72)
    amp = (0.015 + 0.145 * depth) * tentacle * lag_amount
    nx += amp * lag_wave
    ny += amp * 0.72 * cross_wave
    nz += tentacle * lag_amount * (0.10 * math.sin(depth * 5.6 + lag_phase) - 0.05 * depth)

    # During the power stroke, the top of the tentacle bundle follows the bell,
    # while the long ends drag behind in water.
    nx -= x * contraction * tentacle * (0.30 * (1.0 - depth) + 0.16)
    ny -= y * contraction * tentacle * (0.30 * (1.0 - depth) + 0.16)
    nz += contraction * tentacle * (0.14 * (1.0 - depth) - 0.72 * tip)

    # Before the next stroke, the bell opens and draws the strands upward under
    # the umbrella. The lower tips curve inward instead of hanging as a rigid
    # curtain, matching the "gather before clap, straighten during clap" cycle.
    curl = math.sin(angle * 2.3 + depth * 5.8 + lag_phase)
    nx += tuck * tentacle * (0.22 * depth * curl - x * (0.08 + 0.20 * tip))
    ny += tuck * tentacle * (0.18 * depth * math.cos(angle * 2.0 + depth * 4.8 + lag_phase) - y * (0.08 + 0.20 * tip))
    nz += tuck * tentacle * (0.72 * depth + 0.35 * tip)

    # Post-stroke glide: the water stream pulls the long strands into a straighter
    # trailing bundle for a while before the next preparation tuck starts.
    nx -= x * stream * tentacle * (0.10 + 0.14 * depth)
    ny -= y * stream * tentacle * (0.10 + 0.14 * depth)
    nz -= stream * tentacle * (0.22 * depth + 0.48 * tip)

    # A smaller settling wave remains after the bell has opened.
    settle_wave = math.sin(depth * 11.5 + angle * 2.6 + 1.2)
    nx += settle * tentacle * (0.075 * depth * settle_wave)
    ny += settle * tentacle * (0.048 * depth * math.cos(depth * 8.0 + angle))
    nz += settle * tentacle * (0.038 * math.sin(depth * 7.0 + 0.6))

    return Vector((nx, ny, nz))


def set_key_from_deformation(obj, name, base_vertices, bounds, **params):
    key = obj.shape_key_add(name=name)
    for index, co in enumerate(base_vertices):
        key.data[index].co = deform_vertex(co, bounds, **params)
    return key


def keyframe_all(keys, frame, values):
    for key in keys:
        key.value = values.get(key.name, 0.0)
        key.keyframe_insert("value", frame=frame)


def build_animation(obj):
    keys = list(obj.data.shape_keys.key_blocks)[1:]
    obj.data.shape_keys.animation_data_clear()
    obj.data.shape_keys.animation_data_create()
    action = bpy.data.actions.new("realistic_jellyfish_bell_pulse_water_lag")
    obj.data.shape_keys.animation_data.action = action

    frames = [
        (1, {"long_stream_hold": 1.0}),
        (12, {"long_stream_hold": 0.95, "tentacle_lag_left": 0.12}),
        (24, {"long_stream_hold": 0.78, "water_settle_wave": 0.16}),
        (36, {"long_stream_hold": 0.38, "water_settle_wave": 0.30, "anticipation_tuck": 0.24}),
        (46, {"anticipation_tuck": 0.78, "elastic_reopen": 0.22}),
        (52, {"anticipation_tuck": 1.0, "tentacle_lag_right": 0.22}),
        (56, {"power_contract": 1.0, "tentacle_follow_impulse": 0.22}),
        (60, {"power_contract": 0.42, "jet_recoil": 0.72, "tentacle_follow_impulse": 0.55, "long_stream_hold": 0.38}),
        (66, {"long_stream_hold": 1.0, "jet_recoil": 0.22}),
        (76, {"long_stream_hold": 1.0}),
    ]
    for frame, values in frames:
        keyframe_all(keys, frame, values)

    if hasattr(action, "fcurves"):
        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = "BEZIER"
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 76
    bpy.context.scene.render.fps = 24


def setup_preview(obj):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 56
    scene.render.resolution_x = 900
    scene.render.resolution_y = 1100
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("realistic_jellyfish_motion_world")
    world.color = (0.001, 0.004, 0.014)
    scene.world = world
    obj.location = (0, 0, 0.15)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1.0, 1.0, 1.0)

    cam_data = bpy.data.cameras.new("motion_preview_camera")
    cam = bpy.data.objects.new("motion_preview_camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0, -7.2, -0.15)
    cam.rotation_euler = (math.radians(90), 0, 0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 4.6
    scene.camera = cam

    for name, loc, color, energy in [
        ("cyan_motion_key", (-2.2, -3.0, 1.4), (0.18, 0.82, 1.0), 220),
        ("rose_motion_key", (2.0, -2.6, 0.4), (1.0, 0.16, 0.55), 270),
        ("warm_motion_core", (0, -1.5, -0.6), (1.0, 0.28, 0.12), 140),
    ]:
        data = bpy.data.lights.new(name, "POINT")
        data.color = color
        data.energy = energy
        light = bpy.data.objects.new(name, data)
        light.location = loc
        bpy.context.collection.objects.link(light)


def main():
    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(WORK_ASSET))
    for action in list(bpy.data.actions):
      bpy.data.actions.remove(action)
    obj = next((item for item in bpy.context.scene.objects if item.type == "MESH"), None)
    if not obj:
        raise RuntimeError("No mesh found in current jellyfish GLB")

    obj.name = "baked_realistic_jellyfish_motion"
    obj.data.name = "baked_realistic_jellyfish_motion_mesh"
    base_vertices = [vertex.co.copy() for vertex in obj.data.vertices]
    bounds = bounds_for_vertices(base_vertices)
    remove_shape_keys(obj)
    if not obj.data.shape_keys:
        obj.shape_key_add(name="Basis")

    set_key_from_deformation(
        obj,
        "anticipation_tuck",
        base_vertices,
        bounds,
        contraction=0.08,
        rebound=0.0,
        lag_phase=0.4,
        lag_amount=0.30,
        settle=0.0,
        tuck=0.92,
        stream=0.0,
    )
    set_key_from_deformation(
        obj,
        "power_contract",
        base_vertices,
        bounds,
        contraction=1.0,
        rebound=0.0,
        lag_phase=0.9,
        lag_amount=0.08,
        settle=0.0,
        tuck=0.0,
        stream=0.42,
    )
    set_key_from_deformation(
        obj,
        "jet_recoil",
        base_vertices,
        bounds,
        contraction=0.58,
        rebound=0.18,
        lag_phase=1.55,
        lag_amount=0.42,
        settle=0.0,
        tuck=0.0,
        stream=0.76,
    )
    set_key_from_deformation(
        obj,
        "elastic_reopen",
        base_vertices,
        bounds,
        contraction=0.0,
        rebound=1.0,
        lag_phase=2.65,
        lag_amount=0.86,
        settle=0.08,
        tuck=0.52,
        stream=0.0,
    )
    set_key_from_deformation(
        obj,
        "tentacle_lag_left",
        base_vertices,
        bounds,
        contraction=0.0,
        rebound=0.12,
        lag_phase=3.55,
        lag_amount=1.0,
        settle=0.22,
        tuck=0.25,
        stream=0.0,
    )
    set_key_from_deformation(
        obj,
        "tentacle_lag_right",
        base_vertices,
        bounds,
        contraction=0.0,
        rebound=0.08,
        lag_phase=5.15,
        lag_amount=0.92,
        settle=0.25,
        tuck=0.18,
        stream=0.0,
    )
    set_key_from_deformation(
        obj,
        "tentacle_follow_impulse",
        base_vertices,
        bounds,
        contraction=0.72,
        rebound=0.0,
        lag_phase=1.9,
        lag_amount=0.24,
        settle=0.0,
        tuck=0.0,
        stream=0.85,
    )
    set_key_from_deformation(
        obj,
        "long_stream_hold",
        base_vertices,
        bounds,
        contraction=0.0,
        rebound=0.0,
        lag_phase=2.2,
        lag_amount=0.12,
        settle=0.0,
        tuck=0.0,
        stream=1.0,
    )
    set_key_from_deformation(
        obj,
        "water_settle_wave",
        base_vertices,
        bounds,
        contraction=0.0,
        rebound=0.0,
        lag_phase=6.2,
        lag_amount=0.65,
        settle=1.0,
        tuck=0.35,
        stream=0.10,
    )
    build_animation(obj)
    setup_preview(obj)

    blend_path = OUT / "jellyfish_realistic_motion.blend"
    glb_path = OUT / "jellyfish_realistic_motion.glb"
    report_path = OUT / "report.json"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        export_animations=True,
        export_lights=False,
        export_cameras=False,
    )
    for frame, name in [
        (1, "post_stroke_long_stream"),
        (24, "long_stream_hold"),
        (46, "slow_tuck_prepare"),
        (52, "full_tuck_before_clap"),
        (56, "power_contract"),
        (66, "back_to_long_stream"),
    ]:
        scene = bpy.context.scene
        scene.frame_set(frame)
        scene.render.filepath = str(OUT / f"preview_{frame:03d}_{name}.png")
        bpy.ops.render.render(write_still=True)
    report = {
        "workflow": "refine_baked_jellyfish_motion",
        "source_asset": str(WORK_ASSET),
        "glb": str(glb_path),
        "blend": str(blend_path),
        "shape_keys": [key.name for key in obj.data.shape_keys.key_blocks],
        "frames": {
            "1": "rest",
            "11": "fast bell contraction / power stroke",
            "22": "elastic reopen",
            "33": "tentacle water lag",
        },
        "reference_notes": [
            "fast bell contraction creates propulsion",
            "bell relaxation is slower/passive",
            "tentacles lag behind the bell and continue waving during drift",
        ],
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(glb_path, WORK_ASSET)
    print("SAVED", glb_path)
    print("UPDATED", WORK_ASSET)
    print("SHAPE_KEYS", report["shape_keys"])


if __name__ == "__main__":
    main()
