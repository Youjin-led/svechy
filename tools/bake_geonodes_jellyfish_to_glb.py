from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "attempts" / "sketchfab_geonodes_jellyfish_baked_v2"
OUT.mkdir(parents=True, exist_ok=True)

SOURCE = Path(
    r"C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2\assets\sketchfab_jellyfish_deivid\source\Jellyfish\Jellyfish.blend"
)
SAMPLE_FRAMES = [1, 13, 25, 37, 49, 61, 73, 85, 97, 109, 121, 133, 145, 157, 169, 181, 193]
FPS = 24


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def evaluated_mesh_at(obj, frame):
    scene = bpy.context.scene
    scene.frame_set(frame)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(eval_obj, depsgraph=depsgraph)
    return mesh


def copy_materials(source_obj, target_obj):
    for slot in source_obj.material_slots:
        if slot.material:
            target_obj.data.materials.append(slot.material.copy())


def make_render_material(obj):
    mat = bpy.data.materials.new("baked_jellyfish_reference_translucent")
    mat.use_nodes = True
    mat.blend_method = "BLEND"
    mat.show_transparent_back = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.92, 0.58, 1.0, 0.46)
        bsdf.inputs["Alpha"].default_value = 0.46
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (0.6, 0.16, 1.0, 1)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 0.45
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.52
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def animate_shape_keys(obj):
    action = obj.data.shape_keys.animation_data_create().action
    if not action:
        action = bpy.data.actions.new("baked_geonodes_jellyfish_morph_cycle")
        obj.data.shape_keys.animation_data.action = action
    keys = list(obj.data.shape_keys.key_blocks)[1:]
    for i, key in enumerate(keys):
        for other in keys:
            other.value = 0.0
        prev_frame = 1 + max(0, i - 1) * 6
        hit_frame = 1 + i * 6
        next_frame = 1 + min(len(keys) - 1, i + 1) * 6
        key.value = 0.0
        key.keyframe_insert("value", frame=prev_frame)
        key.value = 1.0
        key.keyframe_insert("value", frame=hit_frame)
        key.value = 0.0
        key.keyframe_insert("value", frame=next_frame)
    obj.data.shape_keys.animation_data.action.name = "baked_geonodes_jellyfish_morph_cycle"


def setup_preview_scene(obj):
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 1 + (len(SAMPLE_FRAMES) - 1) * 6
    scene.render.fps = FPS
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 80
    scene.render.resolution_x = 768
    scene.render.resolution_y = 1024
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("baked_jellyfish_deep_world")
    world.color = (0.002, 0.006, 0.018)
    scene.world = world

    obj.rotation_euler = (0, 0, 0)
    obj.location = (0, 0, 1.25)
    obj.scale = (0.74, 0.74, 0.74)

    cam_data = bpy.data.cameras.new("baked_jellyfish_camera")
    cam = bpy.data.objects.new("baked_jellyfish_camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0, -8.0, -1.0)
    cam.rotation_euler = (1.5708, 0, 0)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 5.95
    scene.camera = cam

    for name, loc, color, energy in [
        ("cyan_side", (-2.3, -3.0, 1.7), (0.12, 0.85, 1.0), 260),
        ("rose_side", (2.1, -2.4, 0.8), (1.0, 0.15, 0.54), 330),
        ("warm_core", (0, -1.5, -0.4), (1.0, 0.28, 0.10), 180),
    ]:
        data = bpy.data.lights.new(name, "POINT")
        data.color = color
        data.energy = energy
        light = bpy.data.objects.new(name, data)
        light.location = loc
        bpy.context.collection.objects.link(light)


def main():
    source_obj = next((o for o in bpy.context.scene.objects if o.type == "MESH"), None)
    if not source_obj:
        raise RuntimeError("No mesh object found in source blend")
    basis_mesh = evaluated_mesh_at(source_obj, SAMPLE_FRAMES[0])
    baked = bpy.data.objects.new("baked_geonodes_jellyfish", basis_mesh)
    copy_materials(source_obj, baked)
    bpy.context.collection.objects.link(baked)
    make_render_material(baked)

    baked.shape_key_add(name="Basis")
    base_count = len(baked.data.vertices)
    for frame in SAMPLE_FRAMES[1:]:
        mesh = evaluated_mesh_at(source_obj, frame)
        if len(mesh.vertices) != base_count:
            raise RuntimeError(f"Topology changed at frame {frame}: {len(mesh.vertices)} != {base_count}")
        key = baked.shape_key_add(name=f"frame_{frame:03d}")
        for idx, vert in enumerate(mesh.vertices):
            key.data[idx].co = vert.co
        bpy.data.meshes.remove(mesh)
    for obj in list(bpy.context.scene.objects):
        if obj != baked:
            bpy.data.objects.remove(obj, do_unlink=True)
    animate_shape_keys(baked)
    setup_preview_scene(baked)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "jellyfish_baked.blend"))
    bpy.ops.export_scene.gltf(
        filepath=str(OUT / "jellyfish_baked.glb"),
        export_format="GLB",
        export_animations=True,
        export_lights=True,
        export_cameras=True,
    )
    bpy.context.scene.frame_set(37)
    bpy.ops.render.render(write_still=False)
    bpy.data.images["Render Result"].save_render(filepath=str(OUT / "jellyfish_baked_preview.png"), scene=bpy.context.scene)
    print("SAVED", OUT)


if __name__ == "__main__":
    main()
