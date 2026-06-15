#!/usr/bin/env python3
"""check_tools.py — проверка наличия всех инструментов проекта."""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent

def check_file(path: str, desc: str) -> bool:
    exists = (ROOT / path).exists()
    status = "[OK]" if exists else "[MISSING]"
    print(f"  {status} {desc} ({path})")
    return exists

def check_command(cmd: list, desc: str) -> bool:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        ok = result.returncode == 0
        status = "[OK]" if ok else "[FAIL]"
        print(f"  {status} {desc}")
        if not ok:
            print(f"     stderr: {result.stderr[:200]}")
        return ok
    except FileNotFoundError:
        print(f"  [FAIL] {desc} (command not found)")
        return False
    except Exception as e:
        print(f"  [FAIL] {desc} (error: {e})")
        return False

def main():
    print("=" * 50)
    print("CHECK TOOLS - project tools verification")
    print("=" * 50)
    
    all_ok = True
    
    # --- Files ---
    print("\n[FILES]:")
    files = [
        ("index.html", "Main page"),
        ("package.json", "Package.json"),
        ("main.js", "Main JS"),
        ("styles.css", "Styles"),
        ("AGENTS.md", "Agents"),
        ("PROJECT_RULES.md", "Project rules"),
        ("DECISIONS.md", "Decisions"),
        ("TASKS.md", "Tasks"),
        ("AGENT_MEMORY.md", "Agent memory"),
        ("EXPERIMENTS.md", "Experiments"),
        ("evals/README.md", "Evals README"),
        ("evals/frontend_smoke.md", "Frontend smoke test"),
    ]
    for path, desc in files:
        if not check_file(path, desc):
            all_ok = False
    
    # --- Directories ---
    print("\n[DIRECTORIES]:")
    dirs = [
        ("tools", "Tools"),
        ("evals", "Evals"),
        ("assets", "Assets"),
        ("node_modules", "Node modules"),
        (".git", "Git"),
    ]
    for path, desc in dirs:
        if not check_file(path, desc):
            all_ok = False
    
    # --- Commands ---
    print("\n[COMMANDS]:")
    commands = [
        (["node", "--version"], "Node.js"),
        (["npm.cmd", "--version"], "npm"),
        (["python", "--version"], "Python"),
        (["git", "--version"], "Git"),
        (["uv", "--version"], "uv"),
    ]
    for cmd, desc in commands:
        if not check_command(cmd, desc):
            all_ok = False
    
    # --- Result ---
    print("\n" + "=" * 50)
    if all_ok:
        print("RESULT: ALL OK")
    else:
        print("RESULT: SOME CHECKS FAILED")
    print("=" * 50)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
