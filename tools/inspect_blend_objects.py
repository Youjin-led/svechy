import bpy

print("SCENE_OBJECTS")
for obj in bpy.context.scene.objects:
    name = obj.name
    lower = name.lower()
    if any(key in lower for key in ("spiral_project_card", "vertebra", "spine", "hidden_nih_source", "camera")):
        data_name = obj.data.name if getattr(obj, "data", None) else ""
        print(name, obj.type, data_name, tuple(round(v, 4) for v in obj.location), tuple(round(v, 4) for v in obj.scale))
