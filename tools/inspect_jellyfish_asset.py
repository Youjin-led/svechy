import sys
from pathlib import Path

import bpy
from mathutils import Vector

asset = Path(sys.argv[-1])
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=str(asset))

print("JELLYFISH_ASSET", asset)
for obj in bpy.context.scene.objects:
    data_name = obj.data.name if getattr(obj, "data", None) else ""
    print(obj.name, obj.type, data_name, tuple(round(v, 4) for v in obj.location), tuple(round(v, 4) for v in obj.scale))

mins = Vector((10**9, 10**9, 10**9))
maxs = Vector((-10**9, -10**9, -10**9))
for obj in bpy.context.scene.objects:
    if obj.type != "MESH":
        continue
    for corner in obj.bound_box:
        world = obj.matrix_world @ Vector(corner)
        mins.x = min(mins.x, world.x)
        mins.y = min(mins.y, world.y)
        mins.z = min(mins.z, world.z)
        maxs.x = max(maxs.x, world.x)
        maxs.y = max(maxs.y, world.y)
        maxs.z = max(maxs.z, world.z)

print("BOUNDS", tuple(round(v, 4) for v in mins), tuple(round(v, 4) for v in maxs), "SIZE", tuple(round(v, 4) for v in (maxs - mins)))
print("MATERIALS")
for mat in bpy.data.materials:
    print(mat.name, "alpha", round(mat.diffuse_color[3], 4), "blend", mat.blend_method)
