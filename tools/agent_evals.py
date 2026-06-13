import json
import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def run(command: list[str]) -> tuple[bool, str]:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    return completed.returncode == 0, (completed.stdout + completed.stderr).strip()


def check_file(relative: str) -> tuple[bool, str]:
    return (ROOT / relative).exists(), relative


def check_package_script(name: str) -> tuple[bool, str]:
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    return name in package.get("scripts", {}), f"script:{name}"


def check_memory_rows() -> tuple[bool, str]:
    db = ROOT / ".agent_memory.sqlite3"
    if not db.exists():
        return False, "SQLite memory database exists"
    with sqlite3.connect(db) as connection:
        count = connection.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    return count > 0, f"SQLite memory has rows ({count})"


def main() -> None:
    checks = [
        check_file("AGENTS.md"),
        check_file("AGENT_ROLES.md"),
        check_file("PERMISSIONS.md"),
        check_file("PROJECT_RULES.md"),
        check_file("DECISIONS.md"),
        check_file("EXPERIMENTS.md"),
        check_file("TASKS.md"),
        check_file("evals/agent_operating_loop.md"),
        check_file("evals/meta_learning.md"),
        check_file("evals/visual_qa.md"),
        check_file("evals/max_agent_upgrade.md"),
        check_file("tools/agent_checkpoint.py"),
        check_file("tools/agent_evals.py"),
        check_file("tools/agent_meta.py"),
        check_file("tools/agent_goal.py"),
        check_file("tools/visual_qa.js"),
        check_file("tools/reference_matcher.js"),
        check_file("patterns/README.md"),
        check_file("patterns/threejs-scroll-card-rail.md"),
        check_file("patterns/wet-iridescent-metal.md"),
        check_file("patterns/space-dust-field.md"),
        check_file("patterns/visual-qa-pipeline.md"),
        check_file("patterns/agent-meta-learning.md"),
        check_package_script("visual:qa"),
        check_package_script("visual:match"),
        check_package_script("agent:context"),
        check_package_script("agent:log"),
        check_package_script("agent:checkpoint"),
        check_package_script("agent:evals"),
        check_package_script("agent:meta"),
        check_package_script("agent:goal"),
        check_package_script("scene:status"),
        check_package_script("scene:attempt"),
        check_file("tools/scene_status.py"),
        check_file("tools/scene_attempt.py"),
        check_memory_rows(),
    ]

    tools_ok, _ = run(["npm.cmd", "run", "check:tools"])
    checks.append((tools_ok, "npm run check:tools"))

    failed = False
    for ok, label in checks:
        print(f"[{'OK' if ok else 'FAIL'}] {label}")
        failed = failed or not ok

    if failed:
        raise SystemExit(2)
    print("[OK] Agent evals passed.")


if __name__ == "__main__":
    main()
