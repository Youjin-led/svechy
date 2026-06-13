import json
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
FINAL_FILES = {
    "preview": OUTPUT / "preview.png",
    "blend": OUTPUT / "scene.blend",
    "glb": OUTPUT / "scene.glb",
    "report": OUTPUT / "report.json",
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def describe(path: Path) -> dict:
    exists = path.exists()
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": exists,
        "size_bytes": path.stat().st_size if exists else 0,
        "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds") if exists else None,
    }


def main() -> None:
    status = {name: describe(path) for name, path in FINAL_FILES.items()}
    report_path = FINAL_FILES["report"]
    report = None
    if report_path.exists():
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            report = {"error": f"Invalid report JSON: {error}"}

    print("# Scene Status")
    print("Only these final files represent the current scene:")
    for name, info in status.items():
        marker = "OK" if info["exists"] and info["size_bytes"] > 0 else "MISSING"
        print(f"- [{marker}] {name}: {info['path']} ({info['size_bytes']} bytes, modified={info['modified']})")

    if report:
        print("\n## Report")
        print(f"- status: {report.get('status')}")
        print(f"- workflow: {report.get('workflow')}")
        artifacts = report.get("artifacts") or {}
        for name, path in artifacts.items():
            print(f"- artifact.{name}: {path}")

    attempts = OUTPUT / "attempts"
    if attempts.exists():
        latest = sorted(attempts.iterdir(), reverse=True)[:5]
        if latest:
            print("\n## Recent Attempts")
            for entry in latest:
                print(f"- {entry.name}")


if __name__ == "__main__":
    main()
