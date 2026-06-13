import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOALS_PATH = ROOT / ".agent_goals.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state() -> dict:
    if not GOALS_PATH.exists():
        return {"goals": []}
    return json.loads(GOALS_PATH.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    GOALS_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def next_id(items: list[dict]) -> int:
    return max((item["id"] for item in items), default=0) + 1


def create_goal(args: argparse.Namespace) -> None:
    state = load_state()
    goal = {
        "id": next_id(state["goals"]),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "title": args.title,
        "status": "active",
        "domain": args.domain,
        "strategy": args.strategy,
        "notes": args.notes or "",
        "steps": [],
    }
    state["goals"].append(goal)
    save_state(state)
    print(json.dumps(goal, ensure_ascii=False, indent=2))


def find_goal(state: dict, goal_id: int) -> dict:
    for goal in state["goals"]:
        if goal["id"] == goal_id:
            return goal
    raise SystemExit(f"Goal #{goal_id} not found.")


def add_step(args: argparse.Namespace) -> None:
    state = load_state()
    goal = find_goal(state, args.goal_id)
    step = {
        "id": next_id(goal["steps"]),
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "title": args.title,
        "status": "pending",
        "notes": args.notes or "",
    }
    goal["steps"].append(step)
    goal["updated_at"] = now_iso()
    save_state(state)
    print(json.dumps(step, ensure_ascii=False, indent=2))


def set_step_status(args: argparse.Namespace) -> None:
    state = load_state()
    goal = find_goal(state, args.goal_id)
    for step in goal["steps"]:
        if step["id"] == args.step_id:
            step["status"] = args.status
            step["updated_at"] = now_iso()
            if args.notes:
                step["notes"] = args.notes
            goal["updated_at"] = now_iso()
            save_state(state)
            print(json.dumps(step, ensure_ascii=False, indent=2))
            return
    raise SystemExit(f"Step #{args.step_id} not found in goal #{args.goal_id}.")


def set_goal_status(args: argparse.Namespace) -> None:
    state = load_state()
    goal = find_goal(state, args.goal_id)
    goal["status"] = args.status
    goal["updated_at"] = now_iso()
    if args.notes:
        goal["notes"] = args.notes
    save_state(state)
    print(json.dumps(goal, ensure_ascii=False, indent=2))


def list_goals(args: argparse.Namespace) -> None:
    state = load_state()
    goals = state["goals"]
    if args.status:
        goals = [goal for goal in goals if goal["status"] == args.status]
    if not goals:
        print("[INFO] No goals.")
        return
    for goal in goals:
        done = sum(1 for step in goal["steps"] if step["status"] == "done")
        total = len(goal["steps"])
        print(f"#{goal['id']} [{goal['status']}] {goal['title']} ({done}/{total}) domain={goal['domain']} strategy={goal['strategy']}")


def show_goal(args: argparse.Namespace) -> None:
    state = load_state()
    goal = find_goal(state, args.goal_id)
    print(json.dumps(goal, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local goal/task queue for the project agent.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a goal.")
    create.add_argument("title")
    create.add_argument("--domain", default="coding")
    create.add_argument("--strategy", default="default")
    create.add_argument("--notes")
    create.set_defaults(func=create_goal)

    add = subparsers.add_parser("add-step", help="Add a step to a goal.")
    add.add_argument("goal_id", type=int)
    add.add_argument("title")
    add.add_argument("--notes")
    add.set_defaults(func=add_step)

    step = subparsers.add_parser("step", help="Set step status.")
    step.add_argument("goal_id", type=int)
    step.add_argument("step_id", type=int)
    step.add_argument("status", choices=["pending", "in_progress", "blocked", "done"])
    step.add_argument("--notes")
    step.set_defaults(func=set_step_status)

    status = subparsers.add_parser("status", help="Set goal status.")
    status.add_argument("goal_id", type=int)
    status.add_argument("status", choices=["active", "blocked", "done", "archived"])
    status.add_argument("--notes")
    status.set_defaults(func=set_goal_status)

    list_command = subparsers.add_parser("list", help="List goals.")
    list_command.add_argument("--status")
    list_command.set_defaults(func=list_goals)

    show = subparsers.add_parser("show", help="Show a goal.")
    show.add_argument("goal_id", type=int)
    show.set_defaults(func=show_goal)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
