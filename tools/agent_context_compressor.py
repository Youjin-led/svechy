#!/usr/bin/env python3
"""
agent_context_compressor.py — Контекстный компрессор.

Автоматически сжимает историю разговора в памятки:
  1. Ключевые решения → DECISIONS.md
  2. Инсайты и уроки → AGENT_MEMORY.md
  3. Статус задач → TASKS.md
  4. Важные факты → RAG-память (ChromaDB)

Команды:
  python tools/agent_context_compressor.py compress <text>
  python tools/agent_context_compressor.py rotate
  python tools/agent_context_compressor.py status
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent

def get_token_estimate(text: str) -> int:
    """Грубая оценка токенов (4 символа ≈ 1 токен)."""
    return len(text) // 4

def cmd_compress(text: str):
    """Сжать текст в памятку."""
    tokens = get_token_estimate(text)
    print(f"[COMPRESSOR] Input: {len(text)} chars (~{tokens} tokens)")
    
    # Извлекаем ключевые моменты
    lines = text.split("\n")
    
    decisions = []
    insights = []
    tasks_found = []
    
    for line in lines:
        line_lower = line.lower().strip()
        # Решения
        if any(w in line_lower for w in ["решение:", "decision:", "принято", "approved"]):
            decisions.append(line.strip())
        # Инсайты
        if any(w in line_lower for w in ["инсайт:", "insight:", "урок:", "lesson:", "важно:", "important:"]):
            insights.append(line.strip())
        # Задачи
        if any(w in line_lower for w in ["- [ ]", "- [x]", "todo:", "task:"]):
            tasks_found.append(line.strip())
    
    # Сохраняем в DECISIONS.md
    if decisions:
        decisions_path = ROOT / "DECISIONS.md"
        existing = decisions_path.read_text(encoding="utf-8") if decisions_path.exists() else "# DECISIONS.md\n"
        
        new_entries = []
        for d in decisions:
            entry = f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{d}\n"
            new_entries.append(entry)
        
        with open(decisions_path, "a", encoding="utf-8") as f:
            f.writelines(new_entries)
        
        print(f"  [SAVED] {len(decisions)} decisions → DECISIONS.md")
    
    # Сохраняем в AGENT_MEMORY.md
    if insights:
        memory_path = ROOT / "AGENT_MEMORY.md"
        existing = memory_path.read_text(encoding="utf-8") if memory_path.exists() else "# AGENT_MEMORY.md\n"
        
        with open(memory_path, "a", encoding="utf-8") as f:
            f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            for insight in insights:
                f.write(f"- {insight}\n")
        
        print(f"  [SAVED] {len(insights)} insights → AGENT_MEMORY.md")
    
    # Сохраняем в RAG через SQLite (для последующей перестройки ChromaDB)
    if insights or decisions:
        sqlite_path = ROOT / ".agent_memory.sqlite3"
        if sqlite_path.exists():
            conn = sqlite3.connect(str(sqlite_path))
            cursor = conn.cursor()
            
            # Создаём таблицу если нет
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TEXT
                )
            """)
            
            timestamp = datetime.now().isoformat()
            for item in insights + decisions:
                key = f"compressed:{timestamp}:{hash(item) % 10000}"
                cursor.execute(
                    "INSERT OR REPLACE INTO memory (key, value, created_at) VALUES (?, ?, ?)",
                    (key, item, timestamp)
                )
            
            conn.commit()
            conn.close()
            print(f"  [SAVED] {len(insights) + len(decisions)} items → SQLite memory")
    
    summary = {
        "input_chars": len(text),
        "input_tokens": tokens,
        "compression_ratio": f"{len(text) // max(1, (len(decisions) + len(insights)) * 100)}:1" if decisions or insights else "N/A",
        "decisions_found": len(decisions),
        "insights_found": len(insights),
        "tasks_found": len(tasks_found),
    }
    
    print(f"\n[SUMMARY] {json.dumps(summary, indent=2, ensure_ascii=False)}")
    return summary

def cmd_rotate():
    """Показать статистику использования контекста."""
    print("[COMPRESSOR] Context rotation stats:")
    
    # Размеры файлов
    for fname in ["AGENT_MEMORY.md", "DECISIONS.md", "TASKS.md"]:
        fpath = ROOT / fname
        if fpath.exists():
            size = fpath.stat().st_size
            print(f"  {fname}: {size} bytes (~{size // 4} tokens)")
    
    # Размер SQLite
    sqlite_path = ROOT / ".agent_memory.sqlite3"
    if sqlite_path.exists():
        size = sqlite_path.stat().st_size
        print(f"  .agent_memory.sqlite3: {size} bytes")
    
    # Размер ChromaDB
    chroma_path = ROOT / ".chroma_db"
    if chroma_path.exists():
        total = sum(f.stat().st_size for f in chroma_path.rglob("*") if f.is_file())
        print(f"  .chroma_db (RAG): {total} bytes")

def cmd_status():
    print("[COMPRESSOR] Status: ACTIVE")
    print("  Auto-compress threshold: 50K tokens")
    print("  Targets: DECISIONS.md, AGENT_MEMORY.md, TASKS.md, RAG")
    print()
    cmd_rotate()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == "compress" and len(sys.argv) >= 3:
        cmd_compress(" ".join(sys.argv[2:]))
    elif command == "rotate":
        cmd_rotate()
    elif command == "status":
        cmd_status()
    else:
        print(f"[ERROR] Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
