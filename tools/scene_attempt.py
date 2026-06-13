import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
ATTEMPTS = OUTPUT / "attempts"
FINAL_FILES = ["preview.png", "scene.blend", "scene.glb", "report.json"]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def snapshot(args: argparse.Namespace) -> None:
    ATTEMPTS.mkdir(parents=True, exist_ok=True)
    label = args.label.replace(" ", "-").strip("-") or "scene-attempt"
    target = ATTEMPTS / f"{stamp()}-{label}"
    target.mkdir()

    copied = []
    for filename in FINAL_FILES:
        source = OUTPUT / filename
        if source.exists():
            shutil.copy2(source, target / filename)
            copied.append(filename)

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "label": args.label,
        "copied": copied,
        "note": "This is an archived attempt. The current scene is always output/preview.png, output/scene.blend, output/scene.glb.",
    }
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Saved scene attempt: {target.relative_to(ROOT)}")


def list_attempts(_: argparse.Namespace) -> None:
    if not ATTEMPTS.exists():
        print("[INFO] No scene attempts archived yet.")
        return
    entries = sorted([path for path in ATTEMPTS.iterdir() if path.is_dir()], reverse=True)
    if not entries:
        print("[INFO] No scene attempts archived yet.")
        return
    for entry in entries[:20]:
        manifest = entry / "manifest.json"
        label = ""
        if manifest.exists():
            data = json.loads(manifest.read_text(encoding="utf-8"))
            label = f" - {data.get('label', '')}" if data.get("label") else ""
        print(f"- {entry.name}{label}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive current scene outputs as attempts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot_parser = subparsers.add_parser("snapshot", help="Copy current final scene into output/attempts.")
    snapshot_parser.add_argument("label", nargs="?", default="manual-snapshot")
    snapshot_parser.set_defaults(func=snapshot)

    list_parser = subparsers.add_parser("list", help="List archived scene attempts.")
    list_parser.set_defaults(func=list_attempts)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
