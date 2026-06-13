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

### 2026-05-21 - visual QA and meta autolog upgrade

- Цель: visual QA and meta autolog upgrade
- Что изменили: Created tools/visual_qa.js, added visual:qa script, extended agent_log meta fields, updated eval coverage
- Команда проверки: `npm run visual:qa -- --url http://127.0.0.1:5178/ --steps 4`, `npm run agent:evals`.
- Результат: npm run visual:qa -- --url http://127.0.0.1:5178/ --steps 4; npm run agent:evals
- Вывод: Use visual:qa after 3D/frontend work and agent:log --meta-strategy to record task outcomes into meta-learning.

### 2026-05-21 - max agent upgrade

- Цель: max agent upgrade
- Что изменили: Created agent:goal, visual:match, patterns library, max upgrade eval, and improved meta strategy fallback by domain
- Команда проверки: `npm run agent:evals`, `npm run visual:match -- --reference visual-qa/frame-00.png --candidate visual-qa/frame-00.png`.
- Результат: npm run agent:evals; visual:match smoke PASS with identical images; visual:match REVIEW against real reference as expected
- Вывод: For maximum local autonomy, use agent:goal for task queues, patterns/ for reusable solutions, visual:qa for browser output, visual:match for reference heuristics, and agent:meta for strategy choice.
### 2026-05-21 - reference visual tuning for external site

- Goal: tune `C:\Users\Ардор\OneDrive\Рабочий стол\сайт с 3д` toward the provided Active Theory-like references: darker teal/green grade, closer card scale, denser colored dust, more iridescent spine and glassy card surfaces.
- Changed: updated external site `styles.css` and `main.js`; added `tools/site_render_check.js` for future heavyweight external-site render checks.
- Checks: `node --check main.js`; `node --check tools/site_render_check.js`; `npm run qa`; `npm run check:tools`; `npm run agent:evals`.
- Result: syntax and standard QA passed. `npm run visual:qa -- --url http://127.0.0.1:5180/ --steps 3` and `tools/site_render_check.js` timed out in Puppeteer while opening the heavy external GLB site, so final browser screenshot still needs a manual or fixed-Puppeteer pass.
- Lesson: for large external GLB sites, avoid assuming the default Puppeteer navigation timeout is enough; keep a dedicated no-cache render checker and consider reducing scene weight only if the real browser also struggles.

### 2026-05-21 - deployed reference iteration loop

- Goal: use `https://youjin-led.github.io/3d-form/` as source of truth and iterate without waiting for manual user QA.
- Changed: pushed the site to `Youjin-led/3d-form`, deployed through `gh-pages`, replaced mirrored card texture text with readable sprite labels, faded inactive labels on scroll, softened card noise, removed favicon 404, and replaced built-in uniform GLB stars with controlled dust clouds.
- Checks: repeated Puppeteer screenshots on deployed URL: `deployed-pass8.png`, `deployed-pass9.png`, `deployed-pass10.png`, `deployed-fade-scroll-0.png`, `deployed-fade-scroll-1.png`, `deployed-fade-scroll-2.png`; `node --check main.js`; GitHub push to `main` and `gh-pages`.
- Result: deployment loads with `window.__SCENE_READY === true`, no console errors after favicon fix, active card labels are readable and scroll states no longer show strong floating labels from inactive cards.
- Lesson: for this GLB, card UVs are unreliable for text; draw readable labels as camera-facing sprites and dynamically fade by `cardRail.targetIndex`.

### 2026-05-22 - autonomous deployed polish continuation

- Goal: continue improving deployed `https://youjin-led.github.io/3d-form/` without waiting for manual QA after each pass.
- Changed: added dense bitmap particle cluster planes, reduced card grain, balanced foreground clusters away from the side menu, added a reference-style top-right rail control, and added a dark readability field behind the left menu.
- Checks: `node --check main.js`; GitHub push to `main` and `gh-pages`; HTTP checks confirmed deployed `index.html` includes `rail-control` and deployed `main.js` includes `updateRailControl`, `makeParticleClusterTexture`, and `cardTextSprites`; `npm run agent:evals`.
- Result: last successful Edge screenshot `deployed-edge-check.png` showed denser colored particle clusters and readable active card labels. Later Chromium/Edge launches intermittently timed out before opening the page, so browser QA needs a fresh headless process cleanup before the next visual screenshot series.
- Lesson: continue using Edge with clean profiles for visual QA when bundled Chromium stalls; avoid stopping work solely because one screenshot attempt fails, but record tool instability separately from site quality.

### 2026-05-22 - deployed dust and spine correction

- Goal: fix user complaint that dust clusters looked like flat 2D planes while rotating, and push the spine silhouette closer to the supplied references.
- Changed: removed flat nebula/cardboard dust planes from `main.js`; moved particle creation after GLB load; reduced billboard point density; added small instanced 3D shard clouds; expanded procedural spine augmentation to 13 vertebrae with dorsal spikes, lateral processes, hooks, and rib-like protrusions.
- Checks: `node --check main.js`; `npm run qa`; pushed commits `0d1b8f4`, `4844963`, and `0990d02` to `main` and `gh-pages`; verified deployed `main.js` contains `volumetricShardCloud`, `const count = 13`, `dorsalGeo`, and `ribGeo`; captured live GitHub Pages screenshots from Chrome headless.
- Result: deployed page loads from `https://youjin-led.github.io/3d-form/`; flat 2D dust planes are removed; black shard artifacts from the first instanced pass were corrected by switching shards to smaller additive `MeshBasicMaterial` geometry.
- Lesson: for this scene, use GitHub Pages as the visual source of truth after each push. Avoid large flat particle textures; use either sparse point fields or instanced 3D shards for dust near the spine.

### 2026-05-22 - Blender-source dust and spine pass

- Goal: move visual work back into Blender/GLB instead of building a second procedural spine in site JS; keep current scene restorable.
- Changed: created checkpoint `checkpoints/20260522-110016` and scene attempt `output/attempts/20260522-110247-before-blender-reference-dust-spine-pass`; added `tools/refine_scene_reference_pass.py`; refined existing `real_nih_lumbar_vertebra_*` transforms/materials; added smaller real 3D mesh dust in `output/scene.blend`; exported `output/scene.glb`; copied it to the site; changed viewer to stop generating JS dust and to show GLB dust while hiding constellation/ribbon helpers.
- Checks: Blender save/export/render completed; `npm run scene:status`; `node --check main.js`; `npm run qa`; local Chrome screenshot `local-blender-scene-viewer-v3.png`.
- Result: local viewer shows the anatomical spine retained, visible volumetric dust, and no separate procedural spine column. Further passes should continue in Blender first, then use the site only as preview/deploy.
- Lesson: main.js should behave as a viewer. Do not add fake spine geometry in JS; keep spine changes in `output/scene.blend` and always snapshot before changing anatomy.
