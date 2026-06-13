import sys
from pathlib import Path

import bpy


path = Path(sys.argv[-1])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.fbx(filepath=str(path))

scene = bpy.context.scene
print("FBX", path)
print("FRAME_RANGE", scene.frame_start, scene.frame_end, scene.render.fps)
print("ACTIONS", len(bpy.data.actions))
for action in bpy.data.actions:
    fcurve_count = 0
    if hasattr(action, "fcurves"):
        fcurve_count = len(action.fcurves)
    elif action.layers:
        for slot in action.slots:
            for layer in action.layers:
                for strip in layer.strips:
                    channelbag = strip.channelbag(slot)
                    if channelbag:
                        fcurve_count += len(channelbag.fcurves)
    print("ACTION", action.name, "frames", tuple(round(v, 3) for v in action.frame_range), "curves", fcurve_count)

print("OBJECTS", len(bpy.context.scene.objects))
for obj in bpy.context.scene.objects:
    data = obj.data.name if getattr(obj, "data", None) else ""
    shape_keys = len(obj.data.shape_keys.key_blocks) if getattr(obj, "data", None) and getattr(obj.data, "shape_keys", None) else 0
    anim = bool(obj.animation_data and obj.animation_data.action)
    print("OBJECT", obj.name, obj.type, data, "anim", anim, "shape_keys", shape_keys, "children", len(obj.children))

print("ARMATURES")
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        print("ARMATURE", obj.name, "bones", len(obj.data.bones))
