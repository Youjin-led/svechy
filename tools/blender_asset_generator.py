import argparse
import json
from pathlib import Path

import bpy


def make_material(name, color):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.55
    return material


def add_cube(name, location, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def build_asset(kind, version):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    if kind == "ground":
        material = make_material("grass-green", (0.13, 0.67, 0.27, 1.0))
        add_cube("grass", (0, -0.08, 0), (18, 0.12, 10), material)
        color = 0x22AA44
    elif kind == "car":
        material = make_material("car-red", (1.0 if version >= 2 else 0.2, 0.0, 0.0 if version >= 2 else 1.0, 1.0))
        add_cube("car-body", (-4, 0.45, 0), (2.0, 0.55, 1.0), material)
        color = 0xFF0000 if version >= 2 else 0x3366FF
    else:
        material = make_material("motion-marker", (1.0, 0.0, 0.0, 1.0))
        add_cube("car-motion-marker", (-4, 0.45, 0), (0.2, 0.2, 0.2), material)
        color = 0xFF0000

    return {
        "tool": "Blender",
        "blender_version": bpy.app.version_string,
        "kind": kind,
        "version": version,
        "asset_file": "",
        "object_count": len(bpy.data.objects),
        "dominant_color": color,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", required=True, choices=["ground", "car", "motion"])
    parser.add_argument("--version", required=True, type=int)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metadata = build_asset(args.kind, args.version)

    blend_path = output_path.with_suffix(".blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    metadata["asset_file"] = str(blend_path)
    output_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
