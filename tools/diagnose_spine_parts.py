import json

import bpy
from mathutils import Vector


rows = []
for obj in bpy.context.scene.objects:
    name = obj.name.lower()
    if obj.type != "MESH":
        continue
    if not any(key in name for key in ("vertebra", "lumbar", "nih")):
        continue
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    lo = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    center = (lo + hi) * 0.5
    size = hi - lo
    rows.append({
        "name": obj.name,
        "parent": obj.parent.name if obj.parent else None,
        "center": [round(center.x, 3), round(center.y, 3), round(center.z, 3)],
        "size": [round(size.x, 3), round(size.y, 3), round(size.z, 3)],
        "hide_render": bool(obj.hide_render),
        "hide_viewport": bool(obj.hide_viewport),
    })

print(json.dumps(rows, ensure_ascii=False, indent=2))
