import bpy
from mathutils import Vector


FRAMES = [1, 20, 40, 80, 120, 160, 200]


def mesh_signature(obj, depsgraph):
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    try:
        verts = [v.co.copy() for v in mesh.vertices]
        if not verts:
            return None
        mn = Vector((min(v.x for v in verts), min(v.y for v in verts), min(v.z for v in verts)))
        mx = Vector((max(v.x for v in verts), max(v.y for v in verts), max(v.z for v in verts)))
        sample = []
        step = max(1, len(verts) // 12)
        for i in range(0, len(verts), step):
            v = verts[i]
            sample.append((round(v.x, 5), round(v.y, 5), round(v.z, 5)))
            if len(sample) >= 12:
                break
        return len(verts), tuple(round(x, 5) for x in mn), tuple(round(x, 5) for x in mx), sample
    finally:
        eval_obj.to_mesh_clear()


def main():
    scene = bpy.context.scene
    print("FRAME_RANGE", scene.frame_start, scene.frame_end, scene.render.fps)
    mesh_objects = [o for o in scene.objects if o.type == "MESH"]
    print("MESH_OBJECTS", len(mesh_objects), [o.name for o in mesh_objects[:20]])
    for obj in mesh_objects:
        print("OBJECT", obj.name, "modifiers", [(m.name, m.type, getattr(m, "show_render", None)) for m in obj.modifiers])
        previous = None
        for frame in FRAMES:
            scene.frame_set(frame)
            depsgraph = bpy.context.evaluated_depsgraph_get()
            sig = mesh_signature(obj, depsgraph)
            changed = sig != previous if previous else False
            print("SIG", obj.name, "frame", frame, "changed", changed, sig[:3] if sig else None)
            previous = sig


if __name__ == "__main__":
    main()
