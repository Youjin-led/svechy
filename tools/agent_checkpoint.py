import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS = ROOT / "checkpoints"
FILES = [
    "AGENTS.md",
    "PROJECT_RULES.md",
    "AGENT_MEMORY.md",
    "DECISIONS.md",
    "EXPERIMENTS.md",
    "TASKS.md",
    "AGENT_ROLES.md",
    "PERMISSIONS.md",
    "package.json",
]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def create(args: argparse.Namespace) -> None:
    CHECKPOINTS.mkdir(exist_ok=True)
    target = CHECKPOINTS / stamp()
    target.mkdir()

    copied = []
    for relative in FILES:
        source = ROOT / relative
        if not source.exists():
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(relative)

    db = ROOT / ".agent_memory.sqlite3"
    if db.exists():
        shutil.copy2(db, target / ".agent_memory.sqlite3")
        copied.append(".agent_memory.sqlite3")

    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "label": args.label,
        "files": copied,
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] Created checkpoint: {target}")


def list_checkpoints(_: argparse.Namespace) -> None:
    if not CHECKPOINTS.exists():
        print("[INFO] No checkpoints yet.")
        return
    entries = sorted([path for path in CHECKPOINTS.iterdir() if path.is_dir()], reverse=True)
    if not entries:
        print("[INFO] No checkpoints yet.")
        return
    for entry in entries[:20]:
        manifest = entry / "manifest.json"
        label = ""
        if manifest.exists():
            data = json.loads(manifest.read_text(encoding="utf-8"))
            label = f" - {data.get('label', '')}" if data.get("label") else ""
        print(f"- {entry.name}{label}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and list agent workspace checkpoints.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a checkpoint.")
    create_parser.add_argument("label", nargs="?", default="manual checkpoint")
    create_parser.set_defaults(func=create)

    list_parser = subparsers.add_parser("list", help="List checkpoints.")
    list_parser.set_defaults(func=list_checkpoints)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
