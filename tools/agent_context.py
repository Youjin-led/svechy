import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / ".agent_memory.sqlite3"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def read_text(relative: str) -> str:
    path = ROOT / relative
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def run(command: list[str], timeout: int = 180) -> tuple[int, str]:
    try:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["UV_CACHE_DIR"] = str(ROOT / ".uv-cache")
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=env,
        )
        return completed.returncode, (completed.stdout + completed.stderr).strip()
    except Exception as error:
        return 1, str(error)


def section(title: str) -> None:
    print(f"\n## {title}")


def print_file_presence() -> None:
    required = [
        "AGENTS.md",
        "PROJECT_RULES.md",
        "AGENT_MEMORY.md",
        "DECISIONS.md",
        "EXPERIMENTS.md",
        "TASKS.md",
        "evals/README.md",
        "evals/frontend_smoke.md",
        ".agent_memory.sqlite3",
    ]
    for relative in required:
        status = "OK" if (ROOT / relative).exists() else "MISSING"
        print(f"- [{status}] {relative}")


def print_package_scripts() -> None:
    package_path = ROOT / "package.json"
    if not package_path.exists():
        print("- package.json not found")
        return
    package = json.loads(package_path.read_text(encoding="utf-8"))
    for name, command in package.get("scripts", {}).items():
        print(f"- {name}: `{command}`")


def print_memory_summary() -> None:
    if not DB_PATH.exists():
        print("- SQLite memory database is missing.")
        return
    with sqlite3.connect(DB_PATH) as connection:
        count = connection.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        latest = connection.execute(
            """
            SELECT id, created_at, tags, content
            FROM memories
            ORDER BY id DESC
            LIMIT 5
            """
        ).fetchall()
    print(f"- Database: `{DB_PATH.name}`")
    print(f"- Memories: {count}")
    for memory_id, created_at, tags, content in latest:
        tag_text = f" tags={tags}" if tags else ""
        print(f"- #{memory_id} {created_at}{tag_text}: {content}")


def print_tasks() -> None:
    text = read_text("TASKS.md")
    if not text:
        print("- TASKS.md not found")
        return
    for line in text.splitlines():
        if line.startswith("- ["):
            print(line)


def main() -> None:
    print("# Agent Context")
    print(f"Project root: `{ROOT}`")

    section("Workspace")
    print_file_presence()

    section("Scripts")
    print_package_scripts()

    section("Tools")
    code, output = run(["npm.cmd", "run", "check:tools"], timeout=120)
    print(f"- `npm run check:tools`: {'PASS' if code == 0 else 'FAIL'}")
    if output:
        for line in output.splitlines():
            if line.startswith("["):
                print(f"  {line}")

    section("QA")
    print("- `npm run qa`: not run inside `agent:context`.")
    print(
        "  Run it directly; Puppeteer can timeout when nested under the Python context collector on this Windows setup."
    )

    section("Memory")
    print_memory_summary()

    section("Tasks")
    print_tasks()


if __name__ == "__main__":
    main()
