import argparse
import json
import math
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / ".agent_memory.sqlite3"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_STRATEGIES = {
    "default": {
        "description": "Balanced strategy for ordinary coding, design, and planning tasks.",
        "hyperparams": {
            "temperature": 0.2,
            "max_steps": 8,
            "memory_k": 5,
            "exploration": 0.2,
            "verification": "standard",
        },
    },
    "explorative": {
        "description": "Wider search for ambiguous, visual, research, or novel tasks.",
        "hyperparams": {
            "temperature": 0.65,
            "max_steps": 14,
            "memory_k": 8,
            "exploration": 0.72,
            "verification": "broad",
        },
    },
    "fast": {
        "description": "Low-cost strategy for simple, familiar, or low-risk tasks.",
        "hyperparams": {
            "temperature": 0.1,
            "max_steps": 4,
            "memory_k": 3,
            "exploration": 0.08,
            "verification": "smoke",
        },
    },
    "visual_reference": {
        "description": "Reference-matching strategy for 3D/frontend visual work.",
        "hyperparams": {
            "temperature": 0.35,
            "max_steps": 12,
            "memory_k": 7,
            "exploration": 0.38,
            "verification": "canvas_and_reference",
            "role_order": ["art_director", "shader_materials", "camera_interaction", "final_canvas"],
        },
    },
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS meta_strategies (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            description TEXT NOT NULL,
            hyperparams_json TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            parent_id TEXT
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS meta_episodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            task_descriptor TEXT NOT NULL,
            strategy_id TEXT NOT NULL,
            hyperparams_json TEXT NOT NULL,
            reward REAL NOT NULL,
            cost REAL NOT NULL DEFAULT 0,
            duration REAL NOT NULL DEFAULT 0,
            domain TEXT NOT NULL,
            complexity REAL NOT NULL DEFAULT 0.5,
            novelty REAL NOT NULL DEFAULT 0.5,
            notes TEXT NOT NULL DEFAULT ''
        )
        """
    )
    return connection


def init_strategies(_: argparse.Namespace | None = None) -> None:
    with connect() as connection:
        added = 0
        for strategy_id, strategy in DEFAULT_STRATEGIES.items():
            exists = connection.execute(
                "SELECT 1 FROM meta_strategies WHERE id = ?",
                (strategy_id,),
            ).fetchone()
            if exists:
                continue
            connection.execute(
                """
                INSERT INTO meta_strategies(id, created_at, description, hyperparams_json, active)
                VALUES (?, ?, ?, ?, 1)
                """,
                (
                    strategy_id,
                    now_iso(),
                    strategy["description"],
                    json.dumps(strategy["hyperparams"], ensure_ascii=False, sort_keys=True),
                ),
            )
            added += 1
    print(f"[OK] Meta strategies ready. Added {added}.")


def load_strategies(connection: sqlite3.Connection) -> dict[str, dict]:
    rows = connection.execute(
        """
        SELECT id, description, hyperparams_json
        FROM meta_strategies
        WHERE active = 1
        ORDER BY created_at ASC, id ASC
        """
    ).fetchall()
    return {
        strategy_id: {
            "description": description,
            "hyperparams": json.loads(hyperparams_json),
        }
        for strategy_id, description, hyperparams_json in rows
    }


def strategy_score(row: tuple, complexity: float, novelty: float) -> float:
    reward, cost, duration, episodes, avg_complexity, avg_novelty = row
    efficiency_penalty = min(0.25, cost * 0.02 + duration * 0.002)
    sample_bonus = min(0.08, math.log1p(episodes) * 0.025)
    fit_penalty = abs((avg_complexity or complexity) - complexity) * 0.16
    fit_penalty += abs((avg_novelty or novelty) - novelty) * 0.10
    return reward - efficiency_penalty + sample_bonus - fit_penalty


def choose_strategy(args: argparse.Namespace) -> None:
    init_strategies(None)
    complexity = normalize_complexity(args.complexity, args.task)
    novelty = clamp(args.novelty)
    with connect() as connection:
        strategies = load_strategies(connection)
        domain_rows = connection.execute(
            """
            SELECT strategy_id, AVG(reward), AVG(cost), AVG(duration), COUNT(*), AVG(complexity), AVG(novelty)
            FROM meta_episodes
            WHERE domain = ?
            GROUP BY strategy_id
            """,
            (args.domain,),
        ).fetchall()

    scored: list[tuple[float, str, str]] = []
    rows = domain_rows

    for strategy_id, reward, cost, duration, episodes, avg_complexity, avg_novelty in rows:
        if strategy_id not in strategies:
            continue
        score = strategy_score((reward, cost, duration, episodes, avg_complexity, avg_novelty), complexity, novelty)
        scored.append((score, strategy_id, f"domain:{episodes} episodes"))

    if scored:
        scored.sort(reverse=True)
        _, strategy_id, reason = scored[0]
    else:
        strategy_id = fallback_strategy(args.domain, complexity, novelty)
        reason = "domain fallback heuristic"

    output = {
        "strategy_id": strategy_id,
        "reason": reason,
        "domain": args.domain,
        "complexity": complexity,
        "novelty": novelty,
        **strategies[strategy_id],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def fallback_strategy(domain: str, complexity: float, novelty: float) -> str:
    visual_domains = {"3d", "frontend", "visual", "design", "web"}
    if domain in visual_domains:
        return "visual_reference"
    if complexity < 0.28 and novelty < 0.35:
        return "fast"
    if complexity > 0.68 or novelty > 0.68:
        return "explorative"
    return "default"


def normalize_complexity(value: float | None, task: str) -> float:
    if value is not None:
        return clamp(value)
    length_score = min(1.0, len(task) / 900)
    marker_score = 0.0
    markers = ["сложно", "референс", "3d", "архитект", "само", "интеграция", "память", "shader"]
    lowered = task.lower()
    for marker in markers:
        if marker in lowered:
            marker_score += 0.08
    return clamp(0.22 + length_score * 0.45 + marker_score)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def record_episode(args: argparse.Namespace) -> None:
    init_strategies(None)
    with connect() as connection:
        strategy = connection.execute(
            "SELECT hyperparams_json FROM meta_strategies WHERE id = ?",
            (args.strategy,),
        ).fetchone()
        if not strategy:
            raise SystemExit(f"Unknown strategy: {args.strategy}")
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
                args.task,
                args.strategy,
                strategy[0],
                clamp(args.reward),
                max(0.0, args.cost),
                max(0.0, args.duration),
                args.domain,
                normalize_complexity(args.complexity, args.task),
                clamp(args.novelty),
                args.notes or "",
            ),
        )
    print("[OK] Recorded meta episode.")


def list_strategies(_: argparse.Namespace) -> None:
    init_strategies(None)
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT s.id, s.description, s.hyperparams_json,
                   COUNT(e.id), COALESCE(AVG(e.reward), 0),
                   COALESCE(AVG(e.cost), 0), COALESCE(AVG(e.duration), 0)
            FROM meta_strategies s
            LEFT JOIN meta_episodes e ON e.strategy_id = s.id
            WHERE s.active = 1
            GROUP BY s.id
            ORDER BY s.created_at ASC, s.id ASC
            """
        ).fetchall()
    for strategy_id, description, hyperparams_json, episodes, reward, cost, duration in rows:
        print(f"{strategy_id}: reward={reward:.3f} episodes={episodes} cost={cost:.2f} duration={duration:.1f}s")
        print(f"  {description}")
        print(f"  {hyperparams_json}")


def stats(_: argparse.Namespace) -> None:
    init_strategies(None)
    with connect() as connection:
        total = connection.execute("SELECT COUNT(*) FROM meta_episodes").fetchone()[0]
        by_domain = connection.execute(
            """
            SELECT domain, COUNT(*), AVG(reward), AVG(cost), AVG(duration)
            FROM meta_episodes
            GROUP BY domain
            ORDER BY COUNT(*) DESC, domain ASC
            """
        ).fetchall()
    print(f"[INFO] Meta episodes: {total}")
    if by_domain:
        print("[INFO] By domain:")
        for domain, count, reward, cost, duration in by_domain:
            print(f"- {domain}: episodes={count} reward={reward:.3f} cost={cost:.2f} duration={duration:.1f}s")


def improve(args: argparse.Namespace) -> None:
    init_strategies(None)
    with connect() as connection:
        rows = connection.execute(
            """
            SELECT strategy_id, domain, AVG(reward), AVG(cost), AVG(duration), AVG(complexity),
                   AVG(novelty), COUNT(*)
            FROM meta_episodes
            GROUP BY strategy_id, domain
            HAVING COUNT(*) >= ?
            ORDER BY AVG(reward) DESC, COUNT(*) DESC
            """,
            (args.min_episodes,),
        ).fetchall()
        if not rows:
            print("[INFO] Not enough episodes to improve strategies yet.")
            return
        best = rows[0]
        strategy_id, domain, reward, cost, duration, complexity, novelty, episodes = best
        base = connection.execute(
            "SELECT hyperparams_json FROM meta_strategies WHERE id = ?",
            (strategy_id,),
        ).fetchone()
        if not base:
            raise SystemExit(f"Strategy {strategy_id} disappeared.")
        hyperparams = json.loads(base[0])
        hyperparams["max_steps"] = max(3, round(hyperparams.get("max_steps", 8) * (0.92 if cost > 1 else 1.0)))
        hyperparams["memory_k"] = max(3, min(10, round(hyperparams.get("memory_k", 5) + (1 if reward > 0.78 else 0))))
        hyperparams["exploration"] = round(clamp(hyperparams.get("exploration", 0.2) + (0.06 if novelty > 0.62 else -0.03)), 3)
        new_id = f"meta_{domain}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        description = (
            f"Auto-derived from {strategy_id} for domain={domain}; "
            f"avg_reward={reward:.3f}, episodes={episodes}, avg_complexity={complexity:.2f}."
        )
        connection.execute(
            """
            INSERT INTO meta_strategies(id, created_at, description, hyperparams_json, active, parent_id)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (new_id, now_iso(), description, json.dumps(hyperparams, ensure_ascii=False, sort_keys=True), strategy_id),
        )
    print(json.dumps({"created": new_id, "parent": strategy_id, "description": description, "hyperparams": hyperparams}, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Meta-learning prototype for agent strategy selection.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create default strategies and tables.")
    init.set_defaults(func=init_strategies)

    choose = subparsers.add_parser("choose", help="Choose a strategy for a task.")
    choose.add_argument("--task", required=True)
    choose.add_argument("--domain", default="coding")
    choose.add_argument("--complexity", type=float)
    choose.add_argument("--novelty", type=float, default=0.5)
    choose.set_defaults(func=choose_strategy)

    record = subparsers.add_parser("record", help="Record a completed meta episode.")
    record.add_argument("--task", required=True)
    record.add_argument("--strategy", required=True)
    record.add_argument("--reward", type=float, required=True)
    record.add_argument("--domain", default="coding")
    record.add_argument("--complexity", type=float)
    record.add_argument("--novelty", type=float, default=0.5)
    record.add_argument("--cost", type=float, default=0.0)
    record.add_argument("--duration", type=float, default=0.0)
    record.add_argument("--notes", default="")
    record.set_defaults(func=record_episode)

    strategies = subparsers.add_parser("strategies", help="List active strategies.")
    strategies.set_defaults(func=list_strategies)

    stat_command = subparsers.add_parser("stats", help="Show meta-learning stats.")
    stat_command.set_defaults(func=stats)

    improve_command = subparsers.add_parser("improve", help="Derive one strategy from accumulated episodes.")
    improve_command.add_argument("--min-episodes", type=int, default=3)
    improve_command.set_defaults(func=improve)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
