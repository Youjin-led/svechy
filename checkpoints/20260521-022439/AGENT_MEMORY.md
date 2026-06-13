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
- 2026-05-20: Для честного показа сцены добавлены `scene:status` и `scene:attempt`; текущей сценой считается только `output/preview.png`, а промежуточные рендеры хранятся в `output/attempts/`.

- 2026-05-20: agent context and log tools: Added project context snapshot and task logging commands Checks: npm run agent:context; npm run agent:status.

- 2026-05-20: orchestration memory upgrade: Added roles, permission control, checkpoints, evals, and active SQLite memory management Checks: npm run agent:evals; npm run qa; npm run memory:db -- prune-candidates --limit 5.

- 2026-05-20: reference 3d spine scene: Created custom Blender scene from reference after external artist fallback Checks: Blender background render; npm run qa; npm run agent:evals.

- 2026-05-20: spine anatomy revision: Rebuilt the central column with anatomy-like vertebra bodies, lips, recesses, side processes, and hooks Checks: Blender background render; npm run qa; npm run agent:evals.

- 2026-05-20: honest scene preview pipeline: Added scene:status and scene:attempt so only output/preview.png is treated as current scene and drafts are archived separately Checks: npm run scene:status; npm run scene:attempt -- list; npm run agent:evals; npm run qa.

- 2026-05-20: 3D scene workflow preference: for future projects, prioritize form/silhouette first, then tune color and lighting to the reference. User explicitly said: 'фокус формами ... цвет подтяни под референс'. --tags 3,workflow,preference

- 2026-05-21: For future 3D/frontend work, run an internal role checklist before final delivery: Art Director, Camera/Interaction Designer, Shader/Materials Specialist, Reference Matcher, Performance QA, Memory Curator, Safety Reviewer. Preferred order: match form/composition first, then color/materials, then camera/interaction, then verify the real final canvas/site output. --tags 3d,frontend,workflow,roles,preference
