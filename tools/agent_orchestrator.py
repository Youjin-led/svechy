#!/usr/bin/env python3
"""
agent_orchestrator.py — Оркестратор агентов.

Распределяет задачи между специализированными агентами:
  - coding: написание кода, рефакторинг
  - 3d: 3D модели, Blender, анимации
  - qa: тестирование, визуальное QA
  - trading: TradeLab, инкубация, риск-контроль
  - memory: RAG-память, SQLite
  - meta: мета-обучение, стратегии

Команды:
  python tools/agent_orchestrator.py dispatch <task_type> <description>
  python tools/agent_orchestrator.py status
  python tools/agent_orchestrator.py agents
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent

AGENTS = {
    "coding": {
        "name": "Coding Agent",
        "description": "Написание и рефакторинг кода",
        "tools": ["node", "python", "npm"],
        "capabilities": ["js", "python", "html", "css"],
    },
    "3d": {
        "name": "3D Agent",
        "description": "3D модели, Blender, анимации",
        "tools": ["blender", "python"],
        "capabilities": ["blender", "glb", "fbx", "three.js"],
        "mcp_server": "3d-artist-server",
    },
    "qa": {
        "name": "QA Agent",
        "description": "Тестирование, визуальное QA",
        "tools": ["node", "puppeteer"],
        "capabilities": ["visual_qa", "smoke_test", "reference_match"],
        "mcp_server": "qa-engineer-server",
    },
    "trading": {
        "name": "TradeLab Agent",
        "description": "Торговая система, инкубация, риск",
        "tools": ["node"],
        "capabilities": ["incubation", "risk_control", "discovery", "news"],
        "scripts": [
            "tradelab:incubate", "tradelab:cycle", "tradelab:discover",
            "tradelab:news", "tradelab:risk", "tradelab:safety"
        ],
    },
    "memory": {
        "name": "Memory Agent",
        "description": "RAG-память, SQLite, чекпоинты",
        "tools": ["python"],
        "capabilities": ["rag", "sqlite", "checkpoint", "vector_search"],
        "scripts": ["rag:search", "rag:add", "rag:rebuild", "memory:db"],
    },
    "meta": {
        "name": "Meta Agent",
        "description": "Мета-обучение, стратегии, самоулучшение",
        "tools": ["python"],
        "capabilities": ["meta_learning", "strategy", "self_improvement"],
        "scripts": ["agent:meta", "agent:goal", "agent:context"],
    },
}

def dispatch(task_type: str, description: str):
    agent = AGENTS.get(task_type)
    if not agent:
        print(f"[ERROR] Unknown agent type: {task_type}")
        print(f"  Available: {', '.join(AGENTS.keys())}")
        return
    
    print(f"[ORCHESTRATOR] Dispatching to {agent['name']}")
    print(f"  Task: {description}")
    print(f"  Capabilities: {', '.join(agent['capabilities'])}")
    print(f"  Tools: {', '.join(agent['tools'])}")
    
    if agent.get("mcp_server"):
        print(f"  MCP Server: {agent['mcp_server']}")
    
    if agent.get("scripts"):
        print(f"  Available scripts: {', '.join(agent['scripts'])}")
    
    # Логируем диспатч
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "agent": task_type,
        "task": description,
        "status": "dispatched"
    }
    
    log_path = ROOT / "data" / "orchestrator_log.json"
    log_path.parent.mkdir(exist_ok=True)
    
    logs = []
    if log_path.exists():
        try:
            logs = json.loads(log_path.read_text())
        except:
            pass
    
    logs.append(log_entry)
    log_path.write_text(json.dumps(logs, indent=2, ensure_ascii=False))
    
    print(f"\n[OK] Task dispatched to {agent['name']}")
    print(f"  Log saved to: data/orchestrator_log.json")

def cmd_status():
    log_path = ROOT / "data" / "orchestrator_log.json"
    if not log_path.exists():
        print("[INFO] No tasks dispatched yet.")
        return
    
    logs = json.loads(log_path.read_text())
    print(f"\nTotal dispatched tasks: {len(logs)}")
    
    # Статистика по агентам
    stats = {}
    for entry in logs:
        agent = entry.get("agent", "unknown")
        stats[agent] = stats.get(agent, 0) + 1
    
    print("\nPer agent:")
    for agent, count in sorted(stats.items()):
        print(f"  {agent}: {count} tasks")
    
    print("\nLast 5 tasks:")
    for entry in logs[-5:]:
        print(f"  [{entry['timestamp'][:19]}] {entry['agent']}: {entry['task'][:60]}")

def cmd_agents():
    print(f"\nAvailable agents ({len(AGENTS)}):")
    print("=" * 60)
    for agent_id, agent in AGENTS.items():
        print(f"\n  [{agent_id}] {agent['name']}")
        print(f"    {agent['description']}")
        print(f"    Capabilities: {', '.join(agent['capabilities'])}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == "dispatch" and len(sys.argv) >= 4:
        dispatch(sys.argv[2], " ".join(sys.argv[3:]))
    elif command == "status":
        cmd_status()
    elif command == "agents":
        cmd_agents()
    else:
        print(f"[ERROR] Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()
