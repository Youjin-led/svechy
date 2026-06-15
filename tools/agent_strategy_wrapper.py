#!/usr/bin/env python3
"""agent_strategy_wrapper.py — обёртка для автоматического выбора стратегии перед задачей.

Использование:
  # Выбрать стратегию для задачи
  uv run python tools/agent_strategy_wrapper.py choose --task "описание" --domain coding

  # Записать результат задачи
  uv run python tools/agent_strategy_wrapper.py record --task "описание" --strategy default --reward 0.9 --domain coding

  # Показать текущие стратегии
  uv run python tools/agent_strategy_wrapper.py strategies
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
META_SCRIPT = ROOT / "tools" / "agent_meta.py"


def _quote(s: str) -> str:
    """Экранирует строку для cmd.exe: оборачивает в кавычки, экранирует внутренние кавычки."""
    return '"' + s.replace('"', '\\"') + '"'


def run_meta(args_list: list[str]) -> dict:
    """Запускает agent_meta.py и возвращает JSON из stdout."""
    # Используем sys.executable через shell, экранируя все аргументы
    meta_path = str(META_SCRIPT)
    quoted_args = " ".join(_quote(a) for a in args_list)
    cmd = f'{_quote(sys.executable)} {_quote(meta_path)} {quoted_args}'
    result = subprocess.run(cmd, capture_output=True, shell=True, timeout=30)
    if result.returncode != 0:
        print(f"[ERROR] meta command failed: {cmd}", file=sys.stderr)
        print(result.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)
    # Декодируем stdout вручную
    stdout = result.stdout.decode("utf-8", errors="replace").strip()
    # Ищем JSON-объект: от первой { до последней }
    import re
    match = re.search(r'\{.*\}', stdout, re.DOTALL)
    if match:
        return json.loads(match.group())
    print(f"[ERROR] No JSON found in meta output:\n{stdout[:500]}", file=sys.stderr)
    sys.exit(1)


def cmd_choose(args: argparse.Namespace) -> None:
    """Выбирает стратегию и выводит результат."""
    meta_args = [
        "choose",
        "--task", args.task,
        "--domain", args.domain,
        "--novelty", str(args.novelty),
    ]
    if args.complexity is not None:
        meta_args += ["--complexity", str(args.complexity)]

    result = run_meta(meta_args)

    # Выводим человекочитаемо
    print(f"\n{'='*50}")
    print(f"STRATEGY SELECTED: {result['strategy_id']}")
    print(f"{'='*50}")
    print(f"  Task:       {args.task}")
    print(f"  Domain:     {args.domain}")
    print(f"  Reason:     {result['reason']}")
    print(f"  Complexity: {result['complexity']:.3f}")
    print(f"  Novelty:    {result['novelty']:.3f}")
    print(f"  Strategy:   {result['description']}")
    print(f"  Params:     temperature={result['hyperparams']['temperature']}, "
          f"max_steps={result['hyperparams']['max_steps']}, "
          f"memory_k={result['hyperparams']['memory_k']}, "
          f"exploration={result['hyperparams']['exploration']}")
    if "role_order" in result["hyperparams"]:
        print(f"  Roles:      {' → '.join(result['hyperparams']['role_order'])}")
    print(f"{'='*50}\n")

    # Также выводим чистый JSON для программного использования
    print("---JSON---")
    print(json.dumps(result, ensure_ascii=False))


def cmd_record(args: argparse.Namespace) -> None:
    """Записывает результат выполненной задачи."""
    meta_args = [
        "record",
        "--task", args.task,
        "--strategy", args.strategy,
        "--reward", str(args.reward),
        "--domain", args.domain,
        "--novelty", str(args.novelty),
        "--cost", str(args.cost),
        "--duration", str(args.duration),
        "--notes", args.notes or "",
    ]
    if args.complexity is not None:
        meta_args += ["--complexity", str(args.complexity)]

    subprocess.run(
        [sys.executable, str(META_SCRIPT)] + meta_args,
        check=True,
        timeout=30,
    )
    print(f"[OK] Episode recorded for task: {args.task[:60]}...")


def cmd_strategies(_: argparse.Namespace) -> None:
    """Показывает список стратегий."""
    subprocess.run(
        [sys.executable, str(META_SCRIPT), "strategies"],
        check=True,
        timeout=30,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Agent strategy wrapper — автоматический выбор стратегии перед задачей."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # choose
    choose = subparsers.add_parser("choose", help="Выбрать стратегию для задачи.")
    choose.add_argument("--task", required=True, help="Описание задачи")
    choose.add_argument("--domain", default="coding",
                        help="Домен: coding, 3d, frontend, tradelab, design, research и т.д.")
    choose.add_argument("--complexity", type=float, help="Сложность 0-1 (опционально)")
    choose.add_argument("--novelty", type=float, default=0.5, help="Новизна 0-1")
    choose.set_defaults(func=cmd_choose)

    # record
    record = subparsers.add_parser("record", help="Записать результат задачи.")
    record.add_argument("--task", required=True, help="Описание задачи")
    record.add_argument("--strategy", required=True, help="ID стратегии")
    record.add_argument("--reward", type=float, required=True, help="Награда 0-1")
    record.add_argument("--domain", default="coding", help="Домен")
    record.add_argument("--complexity", type=float, help="Сложность 0-1")
    record.add_argument("--novelty", type=float, default=0.5, help="Новизна 0-1")
    record.add_argument("--cost", type=float, default=0.0, help="Стоимость")
    record.add_argument("--duration", type=float, default=0.0, help="Длительность в секундах")
    record.add_argument("--notes", default="", help="Заметки")
    record.set_defaults(func=cmd_record)

    # strategies
    strategies = subparsers.add_parser("strategies", help="Показать список стратегий.")
    strategies.set_defaults(func=cmd_strategies)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
