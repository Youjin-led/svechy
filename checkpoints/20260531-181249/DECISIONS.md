# Decisions

## 2026-05-31 - Start trader app as paper trading terminal

Decision: build the first trader-app iteration as a local paper trading simulator with generated market data, visible strategy rules, stop-loss/take-profit, drawdown lock, and no real exchange API.

Reason: the user wants a trader that does not trade into losses, but profit cannot be guaranteed. A simulator makes the strategy inspectable and keeps real funds safe until backtesting and paper results are acceptable.

## 2026-05-31 - Keep agent upgrades project-local by default

Decision: improve the agent through project-local memory, patterns, tasks, and checks before editing global Codex skills or configuration.

Reason: project-local files are transparent, versionable, and already part of this workspace's workflow. Global `~/.codex/skills` changes are useful later, but they affect more than this project and should be done only when the user explicitly wants a reusable global skill.

## 2026-05-27 - ZnakVsem MVP scope

Decision: build `znakvsem.ru` as a PatentVsem-connected trademark catalog MVP, not as a standalone marketplace with user accounts or payments. The first release should include catalog cards, trademark detail pages, MKTU/discount/business filters, RU/EN transliteration search, favorites, a cart-like lead questionnaire, a "place trademark" request form, and a simple staff-only admin for adding/removing/editing signs.

Reason: the formal brief excludes personal accounts and payments, and the user clarified that all buyer leads must return to the existing PatentVsem lead flow. Trademark owners' contacts must stay hidden from buyers. Payments happen outside the site by manually generated QR/payment details.

## 2026-05-27 - ZnakVsem visual direction

Decision: prefer the PatentVsem style if feasible; otherwise use the older OnlineZnak layout patterns recolored and restyled closer to PatentVsem. The Yandex Disk archive of `onlineznak.ru_old_disign` is only a visual/layout reference, not the primary product source.

Reason: the user wants ZnakVsem to feel like an additional PatentVsem tab rather than an isolated Nikolai-style marketplace, while still preserving useful OnlineZnak catalog patterns.

## 2026-05-27 - ZnakVsem content source

Decision: use the first 30 trademark entries from `https://patentvsem.ru/tovarniy-znak` as starter catalog content. Each entry should keep its direct Rospatent link where available. MKTU descriptions will be provided by the user later.

Reason: the user explicitly chose PatentVsem's existing first 30 signs as the initial dataset, and PatentVsem already has direct Rospatent references.

## 2026-05-26 - Use Blender-built jellyfish for 3d-form-2 work copy

Decision: replace project cards in `3d-form-2_work_v2` with Blender-built jellyfish geometry exported in the scene GLB, while preserving `spiral_project_card_*_image` object names as movement/rail anchors.

Reason: the user explicitly wanted models like the spine pipeline rather than Three.js placeholders. Available external model sources required authentication/account flows for download, while Blender-built geometry allows immediate local iteration, exact palette matching, and no new licensing or dependency risk.

## 2026-05-25 - Keep PatentVsem rewrite static and isolated

Decision: build the Tilda rewrite as a dependency-free static site under `сайты Игорька/patentvsem-handmade/`, with handwritten HTML/CSS/JS and no Tilda UI runtime.

Reason: the user asked for a separate project that must not mix with the existing 3D work. The original site's lead routing is still Tilda-based, so forms temporarily post to the discovered Tilda endpoint/service ids until a dedicated backend or CRM integration is chosen.

## 2026-05-20 - Начать с markdown-памяти вместо векторной базы

Решение: использовать `AGENT_MEMORY.md`, `PROJECT_RULES.md`, `DECISIONS.md`, `EXPERIMENTS.md` и `TASKS.md` как первый слой внешней памяти.

Причина: это надежно, прозрачно, не требует сети и новых зависимостей. Векторную память можно добавить позже, когда появится стабильный набор заметок и понятный сценарий поиска.

## 2026-05-20 - Оставить существующий `npm run qa` как главный smoke-контур

Решение: опираться на уже имеющийся `qa_check.js`, который поднимает локальный сервер, открывает `index.html` через Puppeteer и проверяет diagnostics.

Причина: в проекте уже есть Puppeteer и Three.js, поэтому проверка визуальной сцены доступна без новой инфраструктуры.

## 2026-05-20 - Добавить SQLite-память без внешних зависимостей

Решение: создать `tools/agent_memory_db.py`, который хранит заметки в `.agent_memory.sqlite3` и использует SQLite FTS5 для поиска.

Причина: это дает более удобную локальную память с поиском и тегами, но не требует сетевой установки пакетов или отдельной базы данных.

## 2026-05-20 - Добавить команды контекста и логирования

Решение: создать `tools/agent_context.py` и `tools/agent_log.py`, подключив их как `npm run agent:context` и `npm run agent:log`.

Причина: агенту нужен быстрый способ восстановить состояние проекта и простой ритуал записи опыта после завершенных задач.

## 2026-05-20 - Добавить оркестрацию, checkpoints и активное управление памятью

Решение: добавить `AGENT_ROLES.md`, `PERMISSIONS.md`, `tools/agent_checkpoint.py`, `tools/agent_evals.py` и расширить SQLite-память полями `importance`, `access_count`, `last_accessed`, `archived`.

Причина: агент должен работать надежнее: разделять роли, сохранять слепки состояния, проверять себя eval-командой и не превращать память в свалку.

## 2026-05-20 - Разделить финальную сцену и черновые attempts

Решение: добавить `tools/scene_status.py` и `tools/scene_attempt.py`, подключив команды `scene:status` и `scene:attempt`.

Причина: промежуточные рендеры не должны смешиваться с текущей сценой. Финальным источником правды являются только `output/preview.png`, `output/scene.blend`, `output/scene.glb`.
## 2026-05-26 - Bake jellyfish body motion in Blender

Decision: jellyfish bell contraction and tentacle motion should be authored/exported in Blender as GLB animation clips, then played on the site with `THREE.AnimationMixer`.

Reason: the user rejected browser-procedural deformation for this direction and asked for animation to come from Blender/model assets, like the imported spine/model workflow. The site may still move the animated objects along its scene routes, but body motion belongs in the GLB.
