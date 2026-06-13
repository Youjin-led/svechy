from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "attempts" / "sketchfab_geonodes_jellyfish_baked_light_v1"
OUT.mkdir(parents=True, exist_ok=True)


def remove_unselected_shape_keys(obj, keep_names):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for index in range(len(obj.data.shape_keys.key_blocks) - 1, -1, -1):
        key = obj.data.shape_keys.key_blocks[index]
        if key.name in keep_names:
            continue
        obj.active_shape_key_index = index
        bpy.ops.object.shape_key_remove()


def rebuild_animation(obj):
    keys = list(obj.data.shape_keys.key_blocks)[1:]
    obj.data.shape_keys.animation_data_clear()
    action = bpy.data.actions.new("baked_geonodes_jellyfish_light_morph_cycle")
    obj.data.shape_keys.animation_data_create()
    obj.data.shape_keys.animation_data.action = action
    step = 8
    for i, key in enumerate(keys):
        for other in keys:
            other.value = 0.0
        before = 1 + max(0, i - 1) * step
        peak = 1 + i * step
        after = 1 + min(len(keys) - 1, i + 1) * step
        key.value = 0.0
        key.keyframe_insert("value", frame=before)
        key.value = 1.0
        key.keyframe_insert("value", frame=peak)
        key.value = 0.0
        key.keyframe_insert("value", frame=after)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 1 + (len(keys) - 1) * step
    scene.render.fps = 24


def main():
    obj = next((item for item in bpy.context.scene.objects if item.type == "MESH"), None)
    if not obj or not obj.data.shape_keys:
        raise RuntimeError("No baked jellyfish mesh with shape keys found")

    key_blocks = list(obj.data.shape_keys.key_blocks)
    morph_names = [key.name for key in key_blocks[1:]]
    selected = []
    if morph_names:
        count = 4
        for i in range(count):
            selected.append(morph_names[round(i * (len(morph_names) - 1) / max(1, count - 1))])
    keep = {"Basis", *selected}
    remove_unselected_shape_keys(obj, keep)
    rebuild_animation(obj)

    obj.name = "baked_geonodes_jellyfish_light"
    obj.data.name = "baked_geonodes_jellyfish_light_mesh"

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "jellyfish_baked_light.blend"))
    bpy.ops.export_scene.gltf(
        filepath=str(OUT / "jellyfish_baked_light.glb"),
        export_format="GLB",
        export_animations=True,
        export_lights=False,
        export_cameras=False,
    )
    print("SAVED", OUT)
    print("KEPT_KEYS", [key.name for key in obj.data.shape_keys.key_blocks])


if __name__ == "__main__":
    main()
