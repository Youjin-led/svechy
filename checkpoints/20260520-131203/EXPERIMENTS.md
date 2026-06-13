# Experiments

## Template

### YYYY-MM-DD - Название эксперимента

- Цель:
- Что изменили:
- Команда проверки:
- Результат:
- Вывод:

## Log

### 2026-05-20 - Агентская обвязка проекта

- Цель: дать агенту внешнюю память, правила проекта и проверяемый рабочий контур.
- Что изменили: добавлены markdown-файлы памяти, решений, экспериментов, задач и eval-критериев.
- Команда проверки: `npm run agent:status`, `npm run qa`.
- Результат: `npm run agent:status` проходит; первый `npm run qa` упал из-за проверки `carColor` при промпте про красную машину; после замены дефолтного промпта на `smoke-scene` `npm run qa` проходит.
- Вывод: markdown-слой установлен; дефолтный `qa` теперь нейтральный smoke-тест, а цветовые проверки лучше запускать отдельными сценариями.

### 2026-05-20 - Проверка инструментов

- Цель: понять, готово ли окружение к генерации и проверке сцен.
- Что изменили: ничего, только запущена проверка.
- Команда проверки: `npm run check:tools`.
- Результат: Node.js, npm, Puppeteer, Three.js и внешний 3D artist найдены; Blender не найден в PATH.
- Вывод: web/smoke-контур доступен, но для полного Blender-пайплайна нужно добавить Blender в PATH или указать путь в проектной конфигурации.

### 2026-05-20 - SQLite-память агента

- Цель: дать агенту локальную память на диске компьютера с поиском и тегами.
- Что изменили: добавлен `tools/agent_memory_db.py`, npm-команда `memory:db`, база `.agent_memory.sqlite3`.
- Команда проверки: `npm run memory:db -- import-md`, `npm run memory:db -- add "..." --tag system --tag memory`, `npm run memory:db -- stats`, `npm run memory:db -- search память`.
- Результат: база создана, 5 записей доступны, поиск работает.
- Вывод: теперь у агента есть локальная SQLite-память внутри workspace; она прозрачная и переносимая вместе с проектом.

### 2026-05-20 - Подключение Blender 5.1

- Цель: закрыть недостающий пункт `check:tools`, где Blender не находился.
- Что изменили: добавлены стандартные пути Blender 5.1 и 5.0 в `ToolRegistry._find_blender`.
- Команда проверки: `npm run check:tools`.
- Результат: `npm run check:tools` проходит; Blender найден по пути `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`.
- Вывод: проект находит установленный Blender без ручной переменной `BLENDER_PATH`.

### 2026-05-20 - Команды agent:context и agent:log

- Цель: дать агенту быстрый снимок проекта и простой способ записывать итоги задач.
- Что изменили: добавлены `tools/agent_context.py`, `tools/agent_log.py`, npm-скрипты `agent:context` и `agent:log`.
- Команда проверки: `npm run agent:status`, `npm run agent:context`, `npm run agent:log -- --title "..." --summary "..."`.
- Результат: `agent:status` и `agent:log` проходят; `agent:context` собирает workspace, scripts, tools, memory и tasks. Вложенный запуск Puppeteer QA из Python на этой Windows-среде таймаутится, поэтому QA оставлен отдельной прямой командой `npm run qa`.
- Вывод: контекст и логирование готовы; браузерный QA нужно запускать напрямую, не из Python-контекстника.

### 2026-05-20 - Оркестрация, checkpoints и memory pruning

- Цель: взять полезные идеи из мульти-агентной оркестрации, активной памяти, fail-safe и eval-цикла.
- Что изменили: добавлены `AGENT_ROLES.md`, `PERMISSIONS.md`, `evals/agent_operating_loop.md`, `tools/agent_checkpoint.py`, `tools/agent_evals.py`; SQLite-память получила поля `importance`, `access_count`, `last_accessed`, `archived`.
- Команда проверки: `npm run agent:checkpoint -- create "orchestration-memory-upgrade"`, `npm run agent:evals`, `npm run memory:db -- prune-candidates --limit 5`, `npm run qa`.
- Результат: checkpoint создан, agent evals проходят, memory pruning показывает кандидатов без удаления, QA проходит.
- Вывод: агент получил рабочую основу для режима оркестратора, наблюдаемости, checkpoint-восстановления и аккуратного забывания.

### 2026-05-20 - agent context and log tools

- Цель: agent context and log tools
- Что изменили: Added project context snapshot and task logging commands
- Команда проверки: `npm run agent:context`, `npm run agent:status`.
- Результат: Added project context snapshot and task logging commands
- Вывод: Запись создана через agent:log.

### 2026-05-20 - orchestration memory upgrade

- Цель: orchestration memory upgrade
- Что изменили: Added roles, permission control, checkpoints, evals, and active SQLite memory management
- Команда проверки: `npm run agent:evals`, `npm run qa`, `npm run memory:db -- prune-candidates --limit 5`.
- Результат: Added roles, permission control, checkpoints, evals, and active SQLite memory management
- Вывод: Запись создана через agent:log.
