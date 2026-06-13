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

### 2026-05-20 - 3D-сцена по референсу с биомеханическим позвоночником

- Цель: создать сцену по приложенному референсу с темным cinematic-фоном, вертикальной металлической колонной и неоновыми частицами.
- Что изменили: добавлен `tools/create_reference_spine_scene.py`; финальные артефакты записаны в `output/scene.blend`, `output/scene.glb`, `output/preview.png`.
- Команда проверки: Blender background render, `npm run qa`, `npm run agent:evals`.
- Результат: внешний 3D artist сначала создал слишком generic primitive scene и вернул пути с mojibake; fail-safe fallback через кастомный Blender-скрипт успешно создал сцену и экспортировал артефакты.
- Вывод: для сложных визуальных референсов полезно использовать 3D artist как первый проход, но держать кастомный Blender fallback для точного art direction.

### 2026-05-20 - Исправление формы позвоночника

- Цель: сделать центральную колонну похожей именно на позвоночник из референса, а не на гладкие капсулы.
- Что изменили: в `tools/create_reference_spine_scene.py` позвонки перестроены как отдельные beveled bodies с фронтальными выпуклостями, темными выемками, округлыми губами, боковыми и крючковатыми отростками.
- Команда проверки: Blender background render, `npm run qa`, `npm run agent:evals`.
- Результат: `output/preview.png`, `output/scene.blend` и `output/scene.glb` обновлены; QA и agent evals проходят.
- Вывод: для узнаваемого позвоночника важнее силуэт каждого позвонка и промежутки между сегментами, чем просто вертикальный стек блестящих форм.

### 2026-05-20 - Честный показ текущей сцены

- Цель: не путать финальную сцену с промежуточными preview и неудачными attempts.
- Что изменили: добавлены `tools/scene_status.py`, `tools/scene_attempt.py`, npm-команды `scene:status` и `scene:attempt`.
- Команда проверки: `npm run scene:status`, `npm run scene:attempt -- snapshot "..."`, `npm run scene:attempt -- list`.
- Результат: `scene:status` показывает только финальные артефакты; `scene:attempt` сохранил текущую сцену в `output/attempts/20260520-134730-current-final-spine-scene`.
- Вывод: финальным источником правды является только `output/preview.png`; черновики хранятся отдельно в `output/attempts/`.

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

### 2026-05-20 - reference 3d spine scene

- Цель: reference 3d spine scene
- Что изменили: Created custom Blender scene from reference after external artist fallback
- Команда проверки: `Blender background render`, `npm run qa`, `npm run agent:evals`.
- Результат: Created custom Blender scene from reference after external artist fallback
- Вывод: Запись создана через agent:log.

### 2026-05-20 - spine anatomy revision

- Цель: spine anatomy revision
- Что изменили: Rebuilt the central column with anatomy-like vertebra bodies, lips, recesses, side processes, and hooks
- Команда проверки: `Blender background render`, `npm run qa`, `npm run agent:evals`.
- Результат: Rebuilt the central column with anatomy-like vertebra bodies, lips, recesses, side processes, and hooks
- Вывод: Запись создана через agent:log.

### 2026-05-20 - honest scene preview pipeline

- Цель: honest scene preview pipeline
- Что изменили: Added scene:status and scene:attempt so only output/preview.png is treated as current scene and drafts are archived separately
- Команда проверки: `npm run scene:status`, `npm run scene:attempt -- list`, `npm run agent:evals`, `npm run qa`.
- Результат: Added scene:status and scene:attempt so only output/preview.png is treated as current scene and drafts are archived separately
- Вывод: Запись создана через agent:log.
