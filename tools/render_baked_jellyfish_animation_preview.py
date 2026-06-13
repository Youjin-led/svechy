from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "attempts" / "sketchfab_geonodes_jellyfish_baked_v2"


def main():
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 97
    scene.render.fps = 24
    scene.render.resolution_x = 540
    scene.render.resolution_y = 720
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.filepath = str(OUT / "jellyfish_baked_animation_preview.mp4")
    bpy.ops.render.render(animation=True)
    print("SAVED", scene.render.filepath)


if __name__ == "__main__":
    main()
