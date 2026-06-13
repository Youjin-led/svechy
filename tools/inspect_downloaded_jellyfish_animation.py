from pathlib import Path

import bpy


scene = bpy.context.scene
print("FRAME_RANGE", scene.frame_start, scene.frame_end, scene.render.fps)
print("ACTIONS", len(bpy.data.actions))
for action in bpy.data.actions:
    fcurve_count = 0
    if hasattr(action, "fcurves"):
        fcurve_count = len(action.fcurves)
    elif action.layers:
        for layer in action.layers:
            for strip in layer.strips:
                channelbag = strip.channelbag(action.slots[0]) if action.slots else None
                if channelbag:
                    fcurve_count += len(channelbag.fcurves)
    print("ACTION", action.name, "frames", tuple(round(v, 3) for v in action.frame_range), "curves", fcurve_count)

print("OBJECTS", len(bpy.context.scene.objects))
for obj in bpy.context.scene.objects:
    data = obj.data.name if getattr(obj, "data", None) else ""
    anim = bool(obj.animation_data and obj.animation_data.action)
    print("OBJECT", obj.name, obj.type, data, "anim", anim, "children", len(obj.children))

print("ARMATURES")
for obj in bpy.context.scene.objects:
    if obj.type == "ARMATURE":
        print("ARMATURE", obj.name, "bones", len(obj.data.bones))
