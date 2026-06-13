# Agent Memory

Этот файл хранит долговременные заметки для работы агента в проекте.

## Stable Preferences

- Пользователь предпочитает русский язык общения.
- Для автономной работы агенту нужна внешняя память, явные проектные правила и проверяемый QA-контур.

## Notes

- 2026-05-20: Создана markdown-обвязка памяти: `AGENTS.md`, `PROJECT_RULES.md`, `DECISIONS.md`, `EXPERIMENTS.md`, `TASKS.md`, `evals/`.
- 2026-05-20: Добавлена локальная SQLite-память `.agent_memory.sqlite3` через `tools/agent_memory_db.py` и команду `npm run memory:db`.
- 2026-05-20: Blender установлен по пути `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`; `ToolRegistry` умеет находить Blender 5.1 и 5.0.
- 2026-05-20: Добавлены команды `agent:context` для снимка проекта и `agent:log` для записи итогов задач в SQLite и markdown-журналы.
- 2026-05-20: Добавлены роли оркестрации, permission control, checkpoints, agent evals и активное управление SQLite-памятью через importance/access_count/archive.

- 2026-05-20: agent context and log tools: Added project context snapshot and task logging commands Checks: npm run agent:context; npm run agent:status.
