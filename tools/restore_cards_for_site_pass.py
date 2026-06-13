import json
from datetime import datetime
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


def restore_cards():
    restored = []
    for obj in bpy.data.objects:
        if "spiral_project_card_" not in obj.name:
            continue
        obj.hide_viewport = False
        obj.hide_render = False
        for child in obj.children:
            child.hide_viewport = False
            child.hide_render = False
        restored.append(obj.name)
    return restored


def save_report(restored):
    report_path = OUTPUT / "report.json"
    report = {}
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
    report["status"] = "PASS"
    report["workflow"] = "restored_scene_cards_for_site_pass"
    report["updated"] = datetime.now().isoformat(timespec="seconds")
    report["artifacts"] = {
        "blend": "output/scene.blend",
        "glb": "output/scene.glb",
        "preview": "output/preview.png",
        "source_script": "tools/restore_cards_for_site_pass.py",
    }
    report["scene_notes"] = [
        "Restored the original Blender card objects before export so the site receives their scene-space placement.",
        "The website must use the GLB transforms directly rather than rebuilding a separate card rail layout.",
    ]
    report["checks"] = [
        f"Restored {len(restored)} spiral_project_card objects",
        "Blender file saved",
        "GLB export completed",
        "Preview render completed",
    ]
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    restored = restore_cards()
    blend_path = OUTPUT / "scene.blend"
    glb_path = OUTPUT / "scene.glb"
    preview_path = OUTPUT / "preview.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    bpy.ops.export_scene.gltf(filepath=str(glb_path), export_format="GLB", export_cameras=True, export_lights=True)
    bpy.context.scene.render.filepath = str(preview_path)
    bpy.ops.render.render(write_still=True)
    save_report(restored)
    print(f"[OK] restored_cards={len(restored)}")
    print(f"[OK] blend={blend_path}")
    print(f"[OK] glb={glb_path}")
    print(f"[OK] preview={preview_path}")


if __name__ == "__main__":
    main()
