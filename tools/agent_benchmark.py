#!/usr/bin/env python3
"""
agent_benchmark.py — Бенчмаркинг агента.

Автоматический замер качества:
  - success rate по типам задач
  - среднее время выполнения
  - cost (токены/API вызовы)
  - сравнение стратегий
  - дашборд

Команды:
  python tools/agent_benchmark.py record <type> <success> <duration> [cost]
  python tools/agent_benchmark.py report
  python tools/agent_benchmark.py dashboard
  python tools/agent_benchmark.py compare <strategy1> <strategy2>
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / ".agent_benchmark.sqlite3"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS benchmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT,
            task_description TEXT,
            strategy TEXT,
            success INTEGER,
            duration_seconds REAL,
            cost REAL,
            timestamp TEXT,
            tokens_used INTEGER
        )
    """)
    conn.commit()
    return conn

def cmd_record(task_type: str, success: str, duration: str, cost: str = "0"):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO benchmarks (task_type, task_description, strategy, success, duration_seconds, cost, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        task_type,
        "manual entry",
        "default",
        1 if success.lower() in ["true", "1", "yes", "success"] else 0,
        float(duration),
        float(cost),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    print(f"[BENCHMARK] Recorded: {task_type} | success={success} | duration={duration}s | cost={cost}")

def cmd_report():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM benchmarks")
    total = cursor.fetchone()[0]
    
    if total == 0:
        print("[BENCHMARK] No data yet. Run 'record' first.")
        conn.close()
        return
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK REPORT — Total tasks: {total}")
    print(f"{'='*60}")
    
    # По типам задач
    cursor.execute("""
        SELECT task_type, 
               COUNT(*) as count,
               SUM(success) as successes,
               AVG(duration_seconds) as avg_duration,
               SUM(cost) as total_cost
        FROM benchmarks
        GROUP BY task_type
        ORDER BY count DESC
    """)
    
    print(f"\n{'Type':<15} {'Count':<8} {'Success':<10} {'Avg Time':<12} {'Cost':<10}")
    print(f"{'-'*55}")
    
    for row in cursor.fetchall():
        task_type, count, successes, avg_dur, total_cost = row
        success_rate = (successes / count * 100) if count > 0 else 0
        print(f"{task_type:<15} {count:<8} {success_rate:.0f}% ({successes}/{count})  {avg_dur:.1f}s{'':<8} ${total_cost:.2f}")
    
    # По стратегиям
    cursor.execute("""
        SELECT strategy,
               COUNT(*) as count,
               SUM(success) as successes,
               AVG(duration_seconds) as avg_duration
        FROM benchmarks
        GROUP BY strategy
        ORDER BY count DESC
    """)
    
    print(f"\n\nBy Strategy:")
    print(f"{'Strategy':<15} {'Count':<8} {'Success':<10} {'Avg Time':<12}")
    print(f"{'-'*45}")
    
    for row in cursor.fetchall():
        strategy, count, successes, avg_dur = row
        success_rate = (successes / count * 100) if count > 0 else 0
        print(f"{strategy:<15} {count:<8} {success_rate:.0f}% ({successes}/{count})  {avg_dur:.1f}s")
    
    # Тренд за последние 7 дней
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cursor.execute("""
        SELECT DATE(timestamp) as day,
               COUNT(*) as count,
               SUM(success) as successes
        FROM benchmarks
        WHERE timestamp > ?
        GROUP BY DATE(timestamp)
        ORDER BY day
    """, (week_ago,))
    
    print(f"\n\nLast 7 days trend:")
    for row in cursor.fetchall():
        day, count, successes = row
        rate = successes / count * 100 if count > 0 else 0
        bar = "█" * int(rate / 10) + "░" * (10 - int(rate / 10))
        print(f"  {day}: {bar} {rate:.0f}% ({successes}/{count})")
    
    conn.close()

def cmd_dashboard():
    """Простой ASCII-дашборд."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM benchmarks")
    total = cursor.fetchone()[0]
    
    if total == 0:
        print("[BENCHMARK] No data yet.")
        conn.close()
        return
    
    print(f"""
╔══════════════════════════════════════════╗
║        AGENT BENCHMARK DASHBOARD         ║
╠══════════════════════════════════════════╣
║  Total tasks: {total:<37} ║
╚══════════════════════════════════════════╝
""")
    
    # Лучшая стратегия
    cursor.execute("""
        SELECT strategy, 
               AVG(success) as success_rate,
               AVG(duration_seconds) as avg_time
        FROM benchmarks
        GROUP BY strategy
        ORDER BY success_rate DESC, avg_time ASC
        LIMIT 1
    """)
    best = cursor.fetchone()
    if best:
        print(f"  Best strategy: {best[0]} ({best[1]*100:.0f}% success, {best[2]:.1f}s avg)")
    
    # Последние 5 записей
    cursor.execute("""
        SELECT task_type, success, duration_seconds, timestamp
        FROM benchmarks
        ORDER BY id DESC
        LIMIT 5
    """)
    
    print(f"\n  Last 5 tasks:")
    for row in cursor.fetchall():
        status = "✅" if row[1] else "❌"
        print(f"    {status} [{row[0]}] {row[2]:.1f}s — {row[3][:19]}")
    
    conn.close()

def cmd_compare(strategy1: str, strategy2: str):
    conn = get_db()
    cursor = conn.cursor()
    
    for strategy in [strategy1, strategy2]:
        cursor.execute("""
            SELECT COUNT(*), SUM(success), AVG(duration_seconds)
            FROM benchmarks
            WHERE strategy = ?
        """, (strategy,))
        
        row = cursor.fetchone()
        if row and row[0] > 0:
            count, successes, avg_dur = row
            rate = successes / count * 100
            print(f"\n  [{strategy}]")
            print(f"    Tasks: {count}")
            print(f"    Success rate: {rate:.1f}%")
            print(f"    Avg time: {avg_dur:.1f}s")
        else:
            print(f"\n  [{strategy}] No data")
    
    conn.close()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == "record" and len(sys.argv) >= 5:
        cmd_record(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "0")
    elif command == "report":
        cmd_report()
    elif command == "dashboard":
        cmd_dashboard()
    elif command == "compare" and len(sys.argv) >= 4:
        cmd_compare(sys.argv[2], sys.argv[3])
    else:
        print(f"[ERROR] Unknown command: {command}")

if __name__ == "__main__":
    main()
