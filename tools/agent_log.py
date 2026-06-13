import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import agent_meta


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / ".agent_memory.sqlite3"
EXPERIMENTS = ROOT / "EXPERIMENTS.md"
AGENT_MEMORY = ROOT / "AGENT_MEMORY.md"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            tags TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
        USING fts5(content, tags, content='memories', content_rowid='id')
        """
    )
    return connection


def add_sqlite_memory(content: str, tags: str) -> int:
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO memories(created_at, tags, content) VALUES (?, ?, ?)",
            (now_iso(), tags, content),
        )
        connection.execute(
            "INSERT INTO memories_fts(rowid, content, tags) VALUES (?, ?, ?)",
            (cursor.lastrowid, content, tags),
        )
        return int(cursor.lastrowid)


def append(path: Path, text: str) -> None:
    if not path.exists():
        path.write_text("", encoding="utf-8")
    with path.open("a", encoding="utf-8") as file:
        file.write(text)


def add_meta_episode(args: argparse.Namespace) -> None:
    if not args.meta_strategy:
        return

    agent_meta.init_strategies(None)
    complexity = agent_meta.normalize_complexity(args.meta_complexity, args.goal or args.title)
    novelty = agent_meta.clamp(args.meta_novelty)
    reward = agent_meta.clamp(args.meta_reward)
    with agent_meta.connect() as connection:
        strategy = connection.execute(
            "SELECT hyperparams_json FROM meta_strategies WHERE id = ?",
            (args.meta_strategy,),
        ).fetchone()
        if not strategy:
            raise SystemExit(f"Unknown meta strategy: {args.meta_strategy}")
        connection.execute(
            """
            INSERT INTO meta_episodes(
                created_at, task_descriptor, strategy_id, hyperparams_json,
                reward, cost, duration, domain, complexity, novelty, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                now_iso(),
                args.goal or args.title,
                args.meta_strategy,
                strategy[0],
                reward,
                max(0.0, args.meta_cost),
                max(0.0, args.meta_duration),
                args.meta_domain,
                complexity,
                novelty,
                args.lesson or args.summary,
            ),
        )
    print("[OK] Logged meta episode")


def build_experiment_entry(args: argparse.Namespace) -> str:
    checks = args.check or ["not specified"]
    check_text = ", ".join(f"`{check}`" for check in checks)
    return (
        f"\n### {today()} - {args.title}\n\n"
        f"- Цель: {args.goal or args.title}\n"
        f"- Что изменили: {args.changed or args.summary}\n"
        f"- Команда проверки: {check_text}.\n"
        f"- Результат: {args.result or args.summary}\n"
        f"- Вывод: {args.lesson or 'Запись создана через agent:log.'}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a completed agent task.")
    parser.add_argument("--title", required=True, help="Short task title.")
    parser.add_argument("--summary", required=True, help="Short outcome summary.")
    parser.add_argument("--goal", help="Task goal.")
    parser.add_argument("--changed", help="What changed.")
    parser.add_argument("--result", help="Verification result.")
    parser.add_argument("--lesson", help="What to remember next time.")
    parser.add_argument("--check", action="append", help="Verification command. Can be repeated.")
    parser.add_argument("--tag", action="append", default=[], help="Memory tag. Can be repeated.")
    parser.add_argument("--no-markdown", action="store_true", help="Only write SQLite memory.")
    parser.add_argument("--meta-strategy", help="Also record a meta-learning episode with this strategy id.")
    parser.add_argument("--meta-reward", type=float, default=0.75, help="Meta reward from 0 to 1.")
    parser.add_argument("--meta-domain", default="coding", help="Meta episode domain.")
    parser.add_argument("--meta-complexity", type=float, help="Meta complexity from 0 to 1.")
    parser.add_argument("--meta-novelty", type=float, default=0.5, help="Meta novelty from 0 to 1.")
    parser.add_argument("--meta-cost", type=float, default=0.0, help="Approximate task cost.")
    parser.add_argument("--meta-duration", type=float, default=0.0, help="Approximate task duration in seconds.")
    args = parser.parse_args()

    tags = ",".join(["task", "agent-log", *args.tag])
    checks = "; ".join(args.check or [])
    memory = f"{args.title}: {args.summary}"
    if checks:
        memory += f" Checks: {checks}."
    if args.lesson:
        memory += f" Lesson: {args.lesson}"

    memory_id = add_sqlite_memory(memory, tags)

    if not args.no_markdown:
        append(AGENT_MEMORY, f"\n- {today()}: {memory}\n")
        append(EXPERIMENTS, build_experiment_entry(args))
    add_meta_episode(args)

    print(f"[OK] Logged task to SQLite memory #{memory_id}")
    if not args.no_markdown:
        print("[OK] Updated AGENT_MEMORY.md and EXPERIMENTS.md")


if __name__ == "__main__":
    main()
