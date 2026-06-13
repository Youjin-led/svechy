from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
ASSET = Path(r"C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2\assets\baked_geonodes_jellyfish.glb")


def main():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.import_scene.gltf(filepath=str(ASSET))
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        coords = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        xs = [v.x for v in coords]
        ys = [v.y for v in coords]
        zs = [v.z for v in coords]
        print("MESH", obj.name, "verts", len(coords), "faces", len(obj.data.polygons))
        print("BBOX_X", min(xs), max(xs))
        print("BBOX_Y", min(ys), max(ys))
        print("BBOX_Z", min(zs), max(zs))
        if obj.data.shape_keys:
            print("SHAPE_KEYS", [key.name for key in obj.data.shape_keys.key_blocks])
        else:
            print("SHAPE_KEYS", [])
        print("MATERIALS", [slot.material.name if slot.material else None for slot in obj.material_slots])
    print("ACTIONS", [action.name for action in bpy.data.actions])


if __name__ == "__main__":
    main()
