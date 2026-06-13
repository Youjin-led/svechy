import sys
from pathlib import Path

import bpy


path = Path(sys.argv[-1])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.fbx(filepath=str(path))

for action in bpy.data.actions:
    print("ACTION", action.name, tuple(round(v, 3) for v in action.frame_range))
    if hasattr(action, "fcurves"):
        curves = action.fcurves
    else:
        curves = []
        for slot in action.slots:
            for layer in action.layers:
                for strip in layer.strips:
                    channelbag = strip.channelbag(slot)
                    if channelbag:
                        curves.extend(channelbag.fcurves)
    for fc in curves:
        print("  CURVE", fc.data_path, fc.array_index, "keys", len(fc.keyframe_points), "firstlast", tuple(round(k.co.y, 4) for k in (fc.keyframe_points[0], fc.keyframe_points[-1])))
