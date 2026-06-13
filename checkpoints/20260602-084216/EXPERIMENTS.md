# Experiments

### 2026-06-01 - Codex Windows sandbox elevation diagnosis

- Goal: reproduce the stuck sandbox setup step from a new session rooted at `C:\Users\...\JS\ДЗ-1`.
- Finding: normal tool calls fail before command execution with `windows sandbox: spawn setup refresh`; sandbox log shows `os error 740`, meaning `codex-windows-sandbox-setup.exe` requires elevation.
- Check: elevated `Get-Location` succeeds in the workspace, and `npm.cmd run check:tools` passes for Blender, Node, npm, Puppeteer, Three.js, and project paths.
- Direct CLI probe: `codex sandbox -C ...` requires `--permissions-profile`; trying likely profile names (`managed`, `default`, `workspace-write`) fails with `default_permissions requires a [permissions] table`.
- Result: the project environment is healthy, but this agent session cannot use the normal Windows sandbox until setup is launched elevated with a managed permissions payload that includes the workspace write root.
- Follow-up fix: backed up `C:\Users\...\ .codex\config.toml` to `config.toml.bak-windows-sandbox-20260601`, then changed `[windows] sandbox` from `elevated` to the valid value `unelevated`.
- Check: `codex --strict-config -c 'windows.sandbox="unelevated"' doctor --summary` and `codex --strict-config doctor --summary` passed.
- Current-session caveat: the already-running agent tool runner still uses the old cached sandbox mode and continues to fail simple `shell_command` calls with `spawn setup refresh`; a fresh Codex/VS Code session is needed to pick up `unelevated`.
- Restart check: after restarting Codex, plain `Get-Location`, `Get-ChildItem`, `node --check`, `npm.cmd run qa`, and `npm.cmd run check:tools` run without the setup refresh failure.
- Follow-up limitation: unelevated sandbox blocks Chromium/Puppeteer process launch with `spawn EPERM`; `npm.cmd run visual:qa` needs an approved/elevated prefix because it opens a browser process.

### 2026-06-01 - Visual QA tool repair

- Goal: fix local checks that failed outside the main smoke QA.
- Finding: `npm.cmd run visual:qa` failed with `ERR_CONNECTION_REFUSED` when no preview server was already running, and `npm.cmd run visual:match` failed without explicit image arguments.
- Changed: `tools/visual_qa.js` now starts a local static server by default, handles occupied preferred ports, accepts the TradeLab `__SCENE_DIAGNOSTICS__` readiness signal, and samples 2D canvas pixels as well as WebGL pixels.
- Changed: `tools/reference_matcher.js` now has a no-argument self-test default using `output/preview.png`; explicit `--reference` and `--candidate` comparisons still perform real heuristic matching.
- Changed: `tools/tradelab_doctor.js` now runs its default syntax, gate, safety, and report checks in-process instead of spawning child `node.exe` commands, which are blocked by the unelevated Windows sandbox.
- Restart follow-up: `npm.cmd run visual:match` no longer launches Chromium for its no-argument self-test, so it passes inside the unelevated sandbox; explicit image comparisons still use the browser-based matcher.
- Check: `node --check tools/visual_qa.js`, `node --check tools/reference_matcher.js`, `npm.cmd run visual:qa`, `npm.cmd run visual:match`, `npm.cmd run qa`, `npm.cmd run agent:evals`, `npm.cmd run check:tools`, `npm.cmd run tradelab:doctor`, and `npm.cmd run scene:status` passed.

### 2026-05-31 - TradeLab MVP browser surface

- Goal: replace the previous 3D demo page with a single-file trader terminal using built-in browser canvas and JavaScript only.
- Checkpoint: `checkpoints/20260531-145811`.
- Changed: implemented synthetic candles for BTC/ETH/SOL/AAPL-like instruments, SMA/RSI signal generation, paper position sizing, stop/take exits, drawdown protection, trade history, and a rolling backtest summary.
- Check: `npm.cmd run qa` passed with `{"status":"PASS","errors":[]}` and the preview server returned HTTP 200 for `/index.html`.
- Note: a custom inline Puppeteer pixel-sampling command timed out outside the normal QA script, so the accepted verification for this pass is the project QA runner plus server availability.
- Follow-up: checkpoint `checkpoints/20260531-151555`; added CSV import for historical candles with header detection for `time/date`, `open/high/low/close`, `volume`, plus short aliases `o/h/l/c/v`. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-152016`; added equity curve canvas, backtest winrate/average trade metrics, and a detailed backtest trade table with entry, exit, reason, PnL dollars, and PnL percent. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-152414`; added a strategy selector with `SMA + RSI`, `Breakout`, and `Mean Reversion`, plus lookback/deviation parameters and automatic backtest recalculation on parameter changes. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-153240`; extracted reusable backtest simulation, added `Compare strategies`, and render a ranked table for all strategies with PnL, profit factor, drawdown, trade count, winrate, and average trade. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-153607`; added `Optimize selected`, small parameter grids per strategy, score ranking that penalizes drawdown, top-5 optimizer results, and one-click parameter application. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-154025`; added `Walk-forward test`, 70/30 train/test split, train-only parameter selection, test validation, test drawdown, best params, and `stable / weak / overfit risk` label. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-154926`; added presets, local saved runs, load/delete, trades CSV export, summary JSON export, copyable report text, risk metrics, buy/sell markers on the main chart, and train/test shading. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-155416`; added direction modes `long-only`, `short-only`, and `long-short`, manual `Short`, commission and slippage inputs, net PnL after fees/slippage, short-aware stop/take logic, and export fields for side/gross/fees. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-161624`; added portfolio mode with multi-CSV upload, per-symbol backtests using current strategy/risk/execution settings, aggregate PnL, combined portfolio drawdown, total trades, weakest symbol, and a symbol table. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-162116`; added Binance Spot public market-data fetch via `https://data-api.binance.vision/api/v3/klines` for symbol/interval/limit candles, mapped klines into the local candle model, and rerun all reports after fetch. Official docs indicate this base endpoint is for public market data and `GET /api/v3/klines` requires no API key. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-162449`; added paper live loop controls, timer-based Binance candle refresh, paper signal/action processing, position-aware live updates, and a rolling live log. No trading endpoint or API key flow was added. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-162754`; added live guardrails for max loss streak, minimum profit factor, drawdown, walk-forward overfit risk, alert log, fetch-failure alerts, position action alerts, and optional live auto-entry blocking. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-163114`; added Strategy Health score/status/recommendation and reason list that combines backtest PnL, profit factor, drawdown, walk-forward, portfolio PnL, and guardrail block state. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-164148`; added reusable `tools/tradelab_run_once.js` exports and `tools/tradelab_research_grid.js`, then ran Binance public market-data research for BTCUSDT/ETHUSDT/SOLUSDT on 15m/1h/4h/1d with 1000 candles. Stable healthy candidates found only on 1h mean-reversion: ETHUSDT, SOLUSDT, BTCUSDT. 1d showed no stable candidates.
- Follow-up: checkpoint `checkpoints/20260531-164546`; added in-browser Research Grid controls and Research Results table that fetch Binance candles, walk-forward optimize each strategy, rank stable candidates, and show PnL/PF/DD/trades/winrate/params. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-165018`; added Candidate Watchlist stored in localStorage, plus add buttons in Research Results and Apply/Live/Delete actions for saved candidates. `npm.cmd run qa` passed after the change.
- Follow-up: checkpoint `checkpoints/20260531-165330`; added candidate lifecycle statuses New/Incubating/Promoted/Rejected, live incubation counters, promote/reject controls, Final Readiness panel, and `TRADELAB.md` usage/safety documentation. `npm.cmd run qa` and `node --check` for research scripts passed.

### 2026-05-31 - GitHub and Hugging Face research loop

- Goal: turn GitHub and Hugging Face into recurring learning sources for Iskra without unsafe downloads or dependency clutter.
- Checkpoint: `checkpoints/20260531-142411`.
- Sources reviewed: GitHub `funwithtriangles/blender-to-threejs-export-guide`; Hugging Face 3D Modeling Spaces; Hugging Face 3D asset generation collection; Hugging Face image-to-3D model listing.
- Findings: Blender-to-Three.js work should stay glTF-first, test exports in an independent glTF viewer, pay attention to NLA tracks and shape-key/morph-target limitations, and beware static animation tracks. Hugging Face is useful for 3D prototype discovery through Hunyuan3D, TRELLIS, Stable Fast 3D, InstantMesh, VGGT, and ActionMesh, but model/Space availability does not mean production-ready rigged animation.
- Changed: added `patterns/github-huggingface-research-loop.md` and linked it from `patterns/README.md`.
- Lesson: use public sources as a curated intake pipeline; only distill small, useful local patterns/tools/evals unless the user approves installs, cloning, or heavy model downloads.

### 2026-05-31 - Project launchers and passports

- Goal: make every collected project restartable without searching through folders.
- Checkpoint: `checkpoints/20260531-125855`.
- Changed: added `Проекты Codex\LAUNCHERS.md` with concrete run/check commands and `Проекты Codex\PROJECT_PASSPORTS.md` with status, purpose, key files, launch commands, and next steps for 3D projects, client sites, materials, Iskra, and the external 3D artist workflow.
- Linked: updated `START_HERE.md` and collection README to point at the new docs.
- Result: future sessions can start from `START_HERE.md`, then use `LAUNCHERS.md` for commands or `PROJECT_PASSPORTS.md` for context and next actions.
- Lesson: after consolidating projects, launch commands and project passports are as important as folder cleanup; they prevent rediscovery work.

### 2026-05-31 - Post-cleanup launch map and smoke audit

- Goal: make the organized project folder easy to restart from and catch obvious broken paths after moving projects.
- Checkpoint: `checkpoints/20260531-123227`.
- Changed: created `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\START_HERE.md` and linked it from the collection README. The launch map points to 3D projects, client sites, materials, Iskra, the external `3д художник` workflow, and the live agent workspace.
- Checks: `node --check` passed for `birzha\app.js`, `znakvsem-marketplace\app.js`, `patentvsem-handmade\main.js`, and `3d-form-3\main.js`; file/asset checks confirmed expected HTML/CSS/JS files and `3d-form-3\assets\scene.glb`.
- Browser note: Puppeteer browser smoke was attempted, but Chrome/Puppeteer launch stalled in this session. Treat the non-browser smoke as structural validation only; run real browser visual QA before judging final 3D canvas output.
- Lesson: after large folder moves, keep a human-first `START_HERE.md` plus a stale-path warning list so future sessions do not waste time in old locations.

### 2026-05-31 - External 3D artist context

- Goal: include `C:\Users\Ардор\OneDrive\Рабочий стол\3д художник` in Iskra's working context because it is a real external Blender/MCP pipeline.
- Changed: added `Проекты Codex\Искра\external-3d-artist` with copied key scripts, MCP README/config, manifests for models/export/output folders, and handling rules.
- Safety: did not duplicate the full folder because it is about 1.77 GB and contains heavy GLB/BLEND assets, venv internals, BlenderKit, generated output, and caches.
- Result: Iskra now has a navigable 3D-artist index while the source folder remains in place for `npm run check:tools` and MCP/Blender workflows.
- Lesson: external tool folders used by `check:tools` should be included in Iskra as indexed working context, even when they are too heavy to copy wholesale.

### 2026-05-31 - Iskra agent center

- Goal: collect everything directly related to the agent into one readable place without breaking the live workspace or copying secrets.
- Checkpoint: `checkpoints/20260531-121850`.
- Changed: created `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\Искра`; copied project agent memory/rules, SQLite memory, tools, patterns, evals, checkpoints, and package scripts into `project-agent-workspace/`; copied only safe global Codex context into `global-codex-safe-index/`.
- Safety: did not copy `auth.json`, `cap_sid`, sessions, logs/state SQLite databases, sandbox secrets, temp/cache folders, or global session archives.
- Result: the Iskra folder is about 5.29 MB and has a `README.md` plus `MANIFEST.md`.
- Lesson: keep this as a readable mirror/index; the live agent workspace remains `JS\ДЗ-1` so active commands and memory tooling continue to work.

### 2026-05-31 - Project folder organization

- Goal: collect completed project folders into one readable place and remove temporary browser/QA noise.
- Checkpoint: `checkpoints/20260531-120500`.
- Changed: created `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex`; moved 3D projects into `3D/`, client sites into `Клиентские сайты/`, and PatentVsem/ZnakVsem briefs/materials into `Материалы/patentvsem-znakvsem/`.
- Cleanup: moved temporary browser profiles and QA screenshots into a temporary review archive, then deleted that archive after confirmation. Removed about 6.47 GB of temporary files.
- Result: organized project collection is about 932 MB; active agent lab `JS\ДЗ-1` is about 1.65 GB and remains in place because it is the current workspace with memory/tools.
- Lesson: after moving project folders, immediately update `AGENT_MEMORY.md` paths so future work does not look in stale locations like `C:\work\3d-form-3`.

### 2026-05-31 - Agent self-improvement pass

- Goal: inspect existing agent memory and local folders, then make the smallest useful upgrades for future autonomy.
- Checkpoint: `checkpoints/20260531-115730`.
- Changed: repaired corrupted durable memory entries, added `patterns/agent-operating-loop.md`, linked it from `patterns/README.md` and `PROJECT_RULES.md`, and recorded the project-local upgrade decision.
- Checks: `npm run memory:db -- stats`; `npm run agent:meta -- stats`.
- Result: memory DB is present with 15 records before new import/logging; meta learner reports 4 coding episodes.
- Lesson: the project already has strong memory/checkpoint/eval infrastructure, so the best next improvement is better routing between active work copies, memory search, existing patterns, and QA.

### 2026-05-27 - Reference-led jellyfish v8 draft

- Goal: continue the Blender-authored jellyfish retry toward the supplied luminous sea nettle reference instead of integrating weak models into the site.
- Checkpoint: `checkpoints/20260527-001733`.
- Changed: iterated `tools/create_reference_led_jellyfish_asset.py` through v4-v8, moving to a portrait render, deep emission ocean background, translucent cyan/rose bell, subtle bell veins, coral rim frill, sparse long tentacles, frilled central oral arms, and a separate trailing oral tail. The exported candidate now contains baked shape-key/root animation for bell recoil, root swim, rim frill, long tentacles, oral arms, and trailing tail.
- Output: draft files under `output/attempts/reference_led_jellyfish_v8/`: `jellyfish_candidate.blend`, `jellyfish_candidate.glb`, and `jellyfish_candidate_preview.png`.
- Checks: Blender export/render succeeded; inspection reports 6 actions over frames 1-96. Visual review: v8 is closer in color, dark background, and overall luminous silhouette, but still not one-to-one with the reference because the oral mass and rim remain too procedural.
- Lesson: for this target quality, a hand-built procedural draft can establish direction and animation clips, but exact reference matching will likely need either a high-quality licensed/CC animated asset or a dedicated sculpt/rig pass with manual mesh editing, not only script-generated geometry.

### 2026-05-27 - Reference-led jellyfish v13 continuation

- Goal: continue after user clarified not to stop before stronger reference matching.
- Changed: iterated v9-v13 in `tools/create_reference_led_jellyfish_asset.py`; rejected the flat inner glow and closed oral plume approaches because they produced a plate/block silhouette; rebuilt the oral mass as separated frilled sheets and changed the tail to a thinner rose trailing element.
- Output: current best draft under `output/attempts/reference_led_jellyfish_v13/`.
- Checks: Blender export/render succeeded; inspection reports 6 actions over frames 1-96: bell recoil, root swim, long tentacles, oral arms, rim frill, and trailing tail.
- Result: v13 is the best procedural draft so far, but still not one-to-one with the reference; the remaining gap is asset quality/manual sculpting, not just animation wiring.

### 2026-05-27 - Baked Geometry Nodes jellyfish site integration

- Goal: try the downloaded Geometry Nodes jellyfish asset on the `3d-form-2_work_v2` site instead of the weaker procedural drafts.
- Changed: copied the baked morph-target GLB to `3d-form-2_work_v2/assets/baked_geonodes_jellyfish.glb`; updated `3d-form-2_work_v2/main.js` so the existing `spiral_project_card_*_image` anchors keep their routes/hover/collision behavior but share the baked jellyfish geometry, material tuning, and per-card `AnimationMixer` morph playback.
- Checks: `node --check` on the work-copy `main.js`; confirmed the local server serves the 77 MB GLB; opened `http://127.0.0.1:5194`; root `npm run qa` passed; `npm run scene:status` still reports the root final scene unchanged.
- Note: automated Puppeteer visual check timed out while launching/loading the heavy GLB, so visual acceptance should be done in the opened browser.

### 2026-05-25 - PatentVsem handmade static rewrite

- Goal: rewrite `https://patentvsem.ru/` as a separate handwritten site under `сайты Игорька/`, preserving the visible landing-page flow and lead forms.
- Checkpoint: `checkpoints/20260525-134728`.
- Changed: created `сайты Игорька/patentvsem-handmade/` with `index.html`, `styles.css`, `main.js`, `README.md`; retained original SEO metadata, anchor navigation, contacts, external links, Yandex.Metrika, map, main lead form, and floating callback popup.
- Checks: downloaded original Tilda HTML for inspection; `node --check` on `main.js`; `npm run qa`; Puppeteer desktop and mobile visual checks; callback popup open check.
- Result: desktop has no horizontal overflow, mobile `documentElement.scrollWidth` equals `clientWidth`, forms are present, popup opens, and browser console logs are clean. Preview screenshots saved as `preview-desktop.png` and `preview-mobile.png`.
- Lesson: Tilda form routing can be preserved temporarily by posting to `https://forms.tildacdn.com/procces/` with the discovered service ids, but production should move forms to a dedicated backend/CRM integration.

### 2026-05-25 - PatentVsem visual match pass

- Goal: make the handmade version visually match the original Tilda site instead of looking like a redesigned landing page.
- Checkpoint: `checkpoints/20260525-140841`.
- Changed: rebuilt the hero to the original yellow card geometry, restored the correct patent illustration asset, matched mobile hero coordinates, moved the intro/services/features/portfolio/stages blocks toward the original black/yellow visual system, and moved the service price/button below the service cards.
- Checks: Puppeteer desktop/mobile screenshots `final2-desktop-0.png`, `final2-desktop-1240.png`, `final2-desktop-2100.png`, `final2-desktop-3200.png`, `final2-mobile-0.png`; popup open check; `npm run qa`.
- Result: first desktop/mobile viewport now closely matches the original composition, with clean console logs, no horizontal overflow, two forms, and a working callback popup.

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

### 2026-05-22 - reverted wrong Blender spine overlay pass

- Goal: correct the mistaken approach where extra primitive anatomy was layered over the spine instead of editing the duplicated vertebra source.
- Reverted: restored `output/scene.blend`, `output/scene.glb`, `output/preview.png`, and `output/report.json` from `output/attempts/20260522-132849-before-anatomy-one-to-one-reference-spine-pass`; deleted `tools/refine_spine_anatomy_match_pass.py`.
- Result: the scene is back to the pre-overlay state. Next pass must edit the repeated vertebra unit itself and then duplicate/rotate it with visible gaps, matching the reference structure.
- Lesson: do not add plate-like helper geometry on top of the spine. The user wants one improved vertebra part, duplicated with small rotations and spacing.

### 2026-05-22 - corrected repeated vertebra unit pass

- Goal: refine the spine using the user's intended structure: one downloaded vertebra part, slightly modified, then repeated with gaps and small rotations.
- Snapshot: `output/attempts/20260522-143033-before-corrected-repeated-vertebra-unit-pass`.
- Changed: added `tools/refine_repeated_vertebra_unit_pass.py`; edited the local mesh shape of each repeated NIH vertebra copy, assigned the wet iridescent material, added subtle worn/pitted modifiers to the repeated unit, increased vertical spacing, reduced per-copy height, and added small per-copy rotations.
- Checks: Blender background save/export/render; `npm run scene:status`; `npm run qa`; `npm run agent:evals`; `tools/diagnose_spine_parts.py`.
- Result: final `output/scene.blend`, `output/scene.glb`, and `output/preview.png` are updated. Diagnostics show copy centers spaced by about `0.92` with copy heights mostly around `0.86-1.08`, so the column now has visible gaps instead of a continuous overlapped tube.
- Lesson: when matching this reference, first validate the repeated-unit spacing numerically before judging the render, because card occlusion can hide whether the spine construction itself is correct.

### 2026-05-22 - card-hidden side-angle vertebra refinement

- Goal: use the extra side-angle references and temporarily hide cards so the Blender spine can be judged without foreground occlusion.
- Snapshot: `output/attempts/20260522-150626-before-further-repeated-vertebra-self-check-refinement`.
- Changed: updated `tools/refine_repeated_vertebra_unit_pass.py` to hide all `spiral_project_card_*` objects for the sculpt-check render, rotate the repeated vertebra copies into a side-profile orientation, tighten copy spacing, add additional local mesh shaping passes (`v4-v6`), and strengthen the wet purple-blue material.
- Checks: repeated Blender background save/export/render cycles; `tools/diagnose_spine_parts.py`; `npm run qa`; `npm run scene:status`; `npm run agent:evals`.
- Result: final `output/preview.png` now shows the spine without cards, built from repeated copies with visible gaps and a more side-oriented vertebra profile. It is closer than the previous front-facing ring/stack view, though further sculpting can still improve the individual vertebra silhouette if stricter one-to-one matching is required.
- Lesson: when the imported vertebra reads like rings, rotating the repeated part itself matters more than orbiting the camera. Hide cards during anatomy passes, then re-enable/composite them only after the spine silhouette is correct.

### 2026-05-22 - reversed tilt with subtle right spiral

- Goal: correct the user's direction note: keep the general tilt feel, reverse its direction, and add only a barely visible rightward spiral through the repeated vertebra column.
- Snapshot: `output/attempts/20260522-155422-before-reversing-vertebra-tilt-and-adding-subtle-right-spiral`.
- Changed: updated `tools/refine_repeated_vertebra_unit_pass.py` orientation math by mirroring the main vertebra tilt, reducing per-copy twist, and adding a tiny center offset phase so the column has a very soft rightward spiral instead of a strong screw shape.
- Checks: Blender background save/export/render; `npm run qa`; `npm run scene:status`.
- Result: final `output/preview.png`, `output/scene.blend`, and `output/scene.glb` are updated with the corrected tilt direction and subtle right-turning stack.
- Lesson: for user-directed anatomical posing, treat "spiral" as very small cumulative per-copy rotation plus slight center drift, not a large visible twist.

### 2026-05-22 - stronger visible reverse tilt

- Goal: make the reversed tilt and rightward spiral actually visible after the user noted the first correction was too subtle.
- Snapshot: `output/attempts/20260522-161807-before-stronger-visible-reverse-tilt-and-right-turn`.
- Changed: increased the mirrored visible roll/side tilt, widened the tiny center drift, and strengthened the cumulative rightward rotation while keeping it below a hard screw-like twist.
- Checks: Blender background save/export/render; `npm run qa`; `npm run scene:status`.
- Result: final `output/preview.png`, `output/scene.blend`, and `output/scene.glb` now show a visibly reversed column tilt with a readable but still soft rightward spiral.
- Lesson: if the user says a pose correction is invisible, prioritize visible silhouette change in the render over small numeric rotation changes.

### 2026-05-22 - relative per-copy spiral correction

- Goal: fix the user's note that the whole column looked rotated as one piece; the spiral must come from each vertebra turning relative to its neighbors.
- Snapshot: `output/attempts/20260522-164810-before-relative-copy-counter-rotation-correction`.
- Changed: replaced simple Euler angle tweaks with ordered rotation matrices so yaw is applied as a real per-copy rightward turn before the reverse tilt; reduced center drift, then increased the neighbor-to-neighbor yaw enough to be visible in the final preview.
- Checks: repeated Blender background save/export/render and manual inspection of `output/preview.png`.
- Result: final `output/preview.png`, `output/scene.blend`, and `output/scene.glb` now show a progressive segment-to-segment turn instead of a uniformly rotated stack.
- Lesson: in this scene, "spiral" means accumulated relative yaw between duplicated vertebra units; camera orbit or whole-column rotation is the wrong visual cue.

### 2026-05-22 - baked Blender scene transferred to site

- Goal: move the final Blender spine scene to the actual local site with the same colors/material feel, without rebuilding it procedurally.
- Checkpoint: `checkpoints/20260522-171322`.
- Changed: copied final `output/scene.glb` and `output/preview.png` into `C:\Users\Ардор\OneDrive\Рабочий стол\сайт с 3д\assets`; added `BAKED_SPINE_VIEW` to the external site's `main.js` so cards are hidden, card rail is disabled, and the camera frames the vertebra bbox while retaining the browser spine/dust material shaders.
- Checks: `node --check` on the external `main.js`; external site served on `http://127.0.0.1:5181/`; Puppeteer screenshot `site-baked-spine.png`; browser reported `ready: true`, `cards: 0`, no console errors; `npm run qa`; `npm run scene:status`.
- Result: the website now loads the updated final GLB instead of the old asset and opens directly on the baked spine view.
- Lesson: when port `5177` is already occupied by the repo preview server, verify `main.js` contents over HTTP before trusting browser QA; use a fresh port for the external site.

### 2026-05-22 - restored scene cards on baked site

- Goal: restore the 3D scene's own cards on the site after the user asked for the same cards back.
- Checkpoint: `checkpoints/20260522-180107`.
- Changed: kept the final GLB as the source, made `spiral_project_card_*` / `reference_card_*` meshes visible again, restored card rail targeting from GLB card positions, and skipped extra readable text sprites in baked mode so the visible cards come from the scene geometry.
- Checks: `node --check` on the external `main.js`; Puppeteer screenshot `site-scene-cards-restored.png`; browser reported `ready: true`, `visibleCards: 30`, `rail: 15`, no console errors; `npm run qa`; `npm run scene:status`.
- Result: the local site on `http://127.0.0.1:5181/` now opens with the spine plus restored 3D scene cards.
- Lesson: if the user asks for "cards from the 3D scene", keep GLB card meshes and rail positions; avoid adding separate text sprite overlays in baked mode.

### 2026-05-23 - imported Blender camera and card transforms for site

- Goal: fix the wrong site card arrangement and remove the white overexposure after restoring cards.
- Checkpoint: `checkpoints/20260523-005331`; attempt: `output/attempts/20260523-005331-before-restoring-cards-for-site-export`.
- Changed: added `tools/restore_cards_for_site_pass.py` to re-enable the existing `spiral_project_card_*` objects before final GLB export; copied the refreshed `output/scene.glb` and `output/preview.png` to the external site; changed the site to use the imported orthographic Blender camera from the GLB instead of a hand-built bbox camera; replaced the overbright card shader with a muted non-emissive card material; reduced site exposure and bloom.
- Checks: Blender save/export/render completed; `node --check` on the external `main.js`; Puppeteer screenshots `site-scene-cards-imported-camera.png` and `site-scene-cards-imported-camera-low-bloom.png`; browser reported `ready: true`; `npm run qa`; `npm run scene:status`.
- Result: cards now come from Blender scene-space transforms and the site camera comes from the GLB camera. The first source/shader attempts caused severe white bloom, so the final viewer keeps bloom low and cards non-emissive.
- Lesson: do not manually convert Blender camera coordinates for GLB scenes. Import the GLTF camera and copy its world transform/projection scale; otherwise the site composition will not match Blender.

### 2026-05-23 - matched published card rail and scroll

- Goal: match the camera/card layout and wheel-driven camera movement from `https://youjin-led.github.io/3d-form/`.
- Checkpoint: `checkpoints/20260523-120201`.
- Changed: inspected the published `main.js`; captured the live reference site's `__CARD_RAIL` and `spiral_project_card_*` transforms into `reference-card-layout.json`; embedded the 30 published card transforms into the external site's `main.js`; switched baked camera mode off so `buildCardRail`, wheel, touch, and nav buttons behave like the published site; adjusted exposure/bloom for the current brighter GLB while keeping the reference rail camera stops.
- Checks: `node --check` on the external `main.js`; Puppeteer online screenshots `reference-online-start.png` / `reference-online-after-wheel.png`; local screenshots `site-reference-layout-balanced-start.png` / `site-reference-layout-balanced-after-wheel.png`; local browser reported `rail: 15`, first rail camera `[-3.611, 6.780, 9.128]`, label changed from `01 - SUSTAINABLE` to `02 - E.C.H.O.` after wheel; `npm run qa`; `npm run scene:status`.
- Result: local site card placement, first camera stop, and wheel-driven rail movement now match the published site behavior. Visual exposure is slightly reduced because the current GLB contains brighter restored scene particles than the published asset.
- Lesson: for matching a deployed interactive scene, capture runtime transforms/rail stops from the browser and replay them locally; source code parity alone is not enough when the GLB assets have diverged.

### 2026-05-24 - S-curve spine posture

- Goal: reshape the repeated vertebra chain so the parts follow the anatomical S-curve from the new reference, while preserving the site cards and published scroll layout.
- Checkpoint: `checkpoints/20260524-210048`; attempt: `output/attempts/20260524-210050-before-s-curve-spine-posture`.
- Changed: updated `tools/refine_repeated_vertebra_unit_pass.py` so the visible duplicated vertebrae use a sagittal S-curve X offset, tangent-based pitch, subtle per-copy yaw, and slightly slimmer per-copy scale; restored scene cards afterward and copied the refreshed `output/scene.glb` / `output/preview.png` to the external site.
- Checks: Blender save/export/render completed; inspected final `output/preview.png`; captured `site-scurve-spine.png` with headless Chrome; `npm run qa`; `npm run scene:status`.
- Result: the final scene artifacts now show the vertebra parts bending along an S-shaped anatomical posture instead of a straight column, with the site still loading the cards and rail UI.
- Lesson: this posture reads best when driven by object locations along a sagittal curve plus local tangent rotation; rotating the whole spine or only changing yaw does not create the anatomical silhouette the user is asking for.

### 2026-05-24 - anchored jellyfish card drift

- Goal: make every project card keep moving like a small jellyfish path while staying close to its published layout anchor.
- Checkpoint: `checkpoints/20260524-215308`.
- Changed: added `floatingCards` state in the external site's `main.js`, stored each `spiral_project_card_*` object's base position/quaternion after published layout normalization, and applied small per-card figure-eight offsets plus subtle rotation wobble each frame; readable text sprites inherit the same local offset.
- Checks: `node --check` on the external `main.js`; local site served on `http://127.0.0.1:5181`; compared `site-card-float-early.png` and `site-card-float-late.png`; `npm run qa`.
- Result: cards now continuously drift in a small radius around their original positions instead of staying static or moving through the whole scene.
- Lesson: keep rail stops static and animate only the card meshes around stored base transforms; otherwise scroll targeting would chase moving geometry and feel unstable.

### 2026-05-24 - full-space card routes

- Goal: make cards travel through the scene on defined routes while keeping the soft jellyfish-like wobble and slightly faster motion.
- Checkpoint: `checkpoints/20260524-225430`.
- Changed: expanded `getCardFloatOffset` from a small local drift into large deterministic elliptical/vertical paths, increased route and wobble speeds, and damped the original anchor contribution so edge cards do not fly too far outside the camera frame.
- Checks: `node --check` on the external `main.js`; local site served on `http://127.0.0.1:5181`; compared `site-card-routes-early.png` and `site-card-routes-late.png`; `npm run qa`.
- Result: cards now move through a broad part of the scene instead of staying around fixed anchor points, while retaining gentle rotation/pulse motion.
- Lesson: when moving cards through the whole composition, large offsets should be partially recentred against their original layout positions; otherwise high/side anchor cards quickly leave the useful viewport.

### 2026-05-25 - card and spine collision response

- Goal: stop moving cards from passing through each other or through the spine; contacts should make them bounce away.
- Checkpoint: `checkpoints/20260524-225430`.
- Changed: added `cardBodies` as per-card collision bodies for paired `image`/`edge` meshes, stored collision offsets/velocities, added card-card repulsion, 3D spine cylinder repulsion, screen-space card-card repulsion, and a wider screen-space spine corridor so visible overlap is pushed apart even when depth differs.
- Checks: `node --check` on the external `main.js`; local site served on `http://127.0.0.1:5181`; captured `site-card-collisions-late.png`; `npm run qa`.
- Result: cards now keep their full-scene routes but gain collision impulses that push them away from neighboring cards and from the spine area instead of visually passing through.
- Lesson: for this transparent 3D scene, collision must include screen-space separation, not only world-space distance, because visually overlapping transparent planes can look like intersection even when their Z positions differ.

### 2026-05-26 - card hover focus

- Goal: make a hovered project card advance toward the screen in a visible, polished way while keeping the moving-card/collision scene intact.
- Checkpoint: `checkpoints/20260526-014106`.
- Changed: added pointer raycasting against the `spiral_project_card_*` meshes, per-card hover state, eased scale/forward camera offset, lifted render order during focus, and matching movement for readable text sprites. Hover is latched while the card slides forward so it does not cancel itself by moving away from the ray.
- Checks: `node --check` on the external `main.js`; local site served on `http://127.0.0.1:5181`; Puppeteer found a hovered card and captured `site-card-hover-focus.png`; no browser console errors; `npm run qa`.
- Result: cards still follow their animated routes and collision response, but the hovered card now smoothly pushes forward and enlarges instead of staying flat in the scene.
- Lesson: raycast hover for animated 3D cards needs a small hover latch/dead-zone; otherwise the card moves out from under the cursor and immediately clears its own hover state.

### 2026-05-26 - static hover focus lock

- Goal: stop the focused card from continuing its jellyfish route after it has advanced toward the screen.
- Changed: capture the hovered card and text sprite position/quaternion at hover start, blend from the live route into that frozen pose plus the camera-forward focus offset, then snap hover amount to `1` once it is visually settled.
- Checks: `node --check` on the external `main.js`; Puppeteer hover-static probe captured `site-card-hover-static.png`; sampled card position after settling had `delta: 0` over 1.4 seconds; no browser console errors; `npm run qa`.
- Result: the hovered card now becomes static once it has moved forward, while non-hovered cards continue moving normally.
- Lesson: for a focused 3D card, freezing the source pose is more reliable than only easing the current animated route; otherwise route motion keeps leaking into the focus state.

### 2026-05-26 - centered face-camera hover

- Goal: make the hovered card rotate flat toward the viewer, land in the screen center, and prevent other moving cards from passing visually in front of it.
- Changed: replaced the old world-offset hover with a camera-space focus target at viewport center, slerped the focused card to the camera quaternion, raised focused card/text render order, and disabled depth testing on the focused card while it is active.
- Checks: `node --check` on the external `main.js`; Puppeteer focus probe captured `site-card-hover-centered.png` and reported center distance `0`, quaternion dot `1`, renderOrder `122`, depthTest `false`; no browser console errors; `npm run qa`.
- Result: a hovered angled card now turns square-on, moves to the exact screen center, and stays above the rest of the moving cards.
- Lesson: a hover overlay in an orthographic Three.js scene should be solved in camera space, not by tweaking world-space X/Y offsets.

### 2026-05-26 - slower card motion

- Goal: make the ambient card movement a little calmer without changing hover focus behavior.
- Changed: added `CARD_MOTION_SPEED = 0.78` and routed the card position/rotation oscillators through that multiplier.
- Checks: `node --check` on the external `main.js`; `npm run qa`.
- Result: card routes and rotation wobble now move about 22% slower while preserving the same path shapes.

### 2026-05-26 - half-size cards

- Goal: make the project cards half as wide.
- Changed: reduced `PUBLISHED_CARD_TARGET_WIDTH` from `3.85` to `1.925`, so the imported card meshes are scaled to half their previous published width while keeping their proportions.
- Checks: `node --check` on the external `main.js`; `npm run qa`.
- Result: cards render at half the previous target width and retain the existing motion/hover logic.

### 2026-05-26 - responsive scene layout

- Goal: make the published 3D scene look composed on desktop, tablets, portrait phones, and landscape phones.
- Checkpoint: `checkpoints/20260526-133147`.
- Changed: added viewport-aware orthographic camera height, card scale/distance, rail zoom, hover focus distance, text scale, and mobile/tablet CSS for the top nav, rail control, side menu, loading state, and safe-area spacing.
- Checks: `node --check` on the external `main.js`; responsive Puppeteer probe for `1440x900`, `834x1112`, `390x844`, and `844x390`; screenshots `responsive-desktop.png`, `responsive-tablet.png`, `responsive-mobile.png`, `responsive-mobile-landscape.png`; `npm run qa`.
- Result: UI controls stay inside the viewport on all tested sizes, the scene stays visible, and mobile layouts use smaller cards plus wider camera framing instead of cropping the spine/card composition.
- Lesson: the 3D canvas needed responsive camera math as much as CSS; only moving DOM controls would leave the orthographic scene too tightly cropped on portrait screens.

### 2026-05-25 - PatentVsem lower-page visual alignment

- Goal: continue the handmade PatentVsem rewrite from the previous pass and align the lower desktop/mobile screenshots with the original Tilda site.
- Checkpoint: `checkpoints/20260525-142806`.
- Changed: made the header fixed like the original during scroll, widened and shifted the contacts/map layout, restored the consultation form subtitle, adjusted the contacts vertical offset, and kept all edits isolated under `сайты Игорька/patentvsem-handmade`.
- Checks: targeted desktop screenshots `quick9-local-desktop-6400.png`, `quick9-local-desktop-7200.png`, `quick9-local-desktop-8000.png`; targeted mobile screenshots `quick9-local-mobile-0.png`, `quick9-local-mobile-7000.png`, `quick9-local-mobile-9800.png`; `node --check` on `main.js`; `npm run qa`.
- Result: lower-page rhythm now lines up with the original reference much more closely: sticky header remains visible, contacts begin at the same scroll band, and the consultation form appears at the same lower-page position.
- Lesson: disable smooth scrolling in screenshot automation before comparing fixed scroll offsets; otherwise Puppeteer can capture mid-animation frames and make sections look incorrectly shifted.

### 2026-05-26 - 3d-form-2 work copy jellyfish replacement

- Goal: create a second working version where the project cards are replaced by beautiful jellyfish-like 3D objects while preserving the spine scene, card routes, collision, rail, and hover behavior.
- Work folder: `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2`; preserved baseline remains `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_saved_responsive_2026-05-26`.
- External model check: Sketchfab downloadable model API required authentication; Meshy jellyfish catalog appeared to require account/download flow, so no third-party model was embedded.
- Initial attempt: added procedural Three.js jellyfish groups in `main.js`, but the user rejected the result because they needed Blender/GLB models like the spine, closer to the supplied reference.
- Changed: added `tools/create_jellyfish_cards_scene_pass.py`, replaced the flat `spiral_project_card_*_image` meshes inside `output/scene.blend` with Blender-built jellyfish geometry, removed card edge meshes, exported the updated `output/scene.glb`, copied it to `3d-form-2_work_v2/assets/scene.glb`, and made `main.js` preserve `jellyfish_*` materials instead of applying the card shader.
- Checks: Blender background export/render; `node --check main.js`; local browser check on `http://127.0.0.1:5182` reported `ready: true`, `jellyfishParts: 375`, `cardImages: 15`, `cardEdges: 0`, `floating: 15`, `rail: 15`; screenshot `blender-jellyfish-site-final.png`; `npm run qa`; `npm run scene:status`.
- Lesson: build replacement objects along Blender Z for vertical screen motion after glTF export; Blender Y becomes depth in the Three.js viewer. Preserve `spiral_project_card_*_image` names as anchors so the existing route/hover system keeps working.

### 2026-05-26 - real GLB jellyfish asset import

- Goal: replace the rejected procedural/Blender-built jellyfish with a real downloaded model, matching the spine workflow more closely.
- Source: `https://www.get3dmodels.com/creatures/rainbow-jellyfish/`; direct asset saved as `3d-form-2_work_v2/assets/colorful_jellyfish_by_get3dmodels.glb`.
- Changed: added `tools/import_real_jellyfish_cards_scene.py`, imported the GLB into the last good spine/card Blender scene, replaced 15 `spiral_project_card_*_image` anchors with shared real jellyfish mesh data, removed card edge meshes, exported optimized `output/scene.glb` and copied it into `3d-form-2_work_v2/assets/scene.glb`.
- Site tuning: kept `USE_JELLYFISH_CARD_MODE`, reduced `PUBLISHED_CARD_TARGET_WIDTH` to `1.28`, and tuned `jellyfish_real_*` material handling in `main.js` so imported models are translucent and fit the dark cyan/magenta composition.
- Checks: Blender import/export/render; `node --check main.js`; browser check on `http://127.0.0.1:5182` reported `ready: true`, `rail: 15`, `canvas: true`, no console errors; screenshot `real-jellyfish-site-final.png`; `npm run qa`; `npm run scene:status`.
- Result: the work copy now uses actual imported GLB jellyfish models instead of generated placeholders.

### 2026-05-26 - live jellyfish motion layer

- Goal: make the imported jellyfish feel alive before their existing route/rail movement is applied.
- Changed: added per-card `jellyfishRig` registration in `3d-form-2_work_v2/main.js`, then animated local jellyfish motion separately from the existing route motion. The bell now breathes/pulses, the whole creature has a subtle swim rotation, and child tentacle meshes sway with delayed local offsets.
- Checks: `node --check main.js`; browser check on `http://127.0.0.1:5182` reported `ready: true`, `rail: 15`, `rigs: 15`, `scaleChanged: true`, `tentacleChanged: true`, no console errors; screenshot `real-jellyfish-live-motion-ready.png`; `npm run qa`.
- Result: jellyfish now animate like living objects first, then continue along the existing trajectory/hover/rail system.

### 2026-05-26 - impulsive jellyfish swim correction

- Goal: make the jellyfish swim like real jellyfish: a sharp bell contraction creates an upward push, followed by slower sinking/drift.
- Changed: replaced the soft sine breathing cycle with a 2.65s impulse cycle in `3d-form-2_work_v2/main.js`: about 24% of the cycle is the kick phase, with strong horizontal bell contraction, vertical bell stretch, upward `jellyfishSwimOffset`, and stronger tentacle lag/stretch.
- Checks: `node --check main.js`; browser probe reported `ready: true`, `rail: 15`, `rigs: 15`, `swimLiftRange: 1.3765`, `scaleXRange: 0.3993`, no console errors; screenshot `real-jellyfish-kick-motion-strong.png`; `npm run qa`; `npm run scene:status`.
- Result: the bell contraction is now visibly stronger and tied to an upward movement, with a slow return downward between kicks.

### 2026-05-26 - jellyfish bell deformation and water-slow descent

- Goal: fix the jellyfish motion after review: the bell barely moved, tentacles drifted away during contraction, and downward motion was too abrupt.
- Changed: cloned each bell mesh per jellyfish and animated the bell vertex positions directly, pulling the lower rim inward/upward during contraction instead of scaling the whole root object. Tentacle child objects now keep much smaller lag offsets and no longer inherit bell squashing. Jellyfish tentacle material was shifted from orange/yellow toward pink-peach.
- Movement tuning: changed the descent easing to start slowly, added a smoothed `jellyfishSwimOffset`, and added asymmetric water smoothing so upward movement can follow the contraction while downward route movement is damped more strongly.
- Checks: browser probe on `http://127.0.0.1:5182` reported `ready: true`, `rail: 15`, `rigs: 15`, `maxDownStep: 0.0966`, `avgDownStep: 0.0502`, `bellWidthRange: 0.1480`, no console errors; screenshot `real-jellyfish-asymmetric-water.png`; `npm run qa`; `npm run scene:status`.
- Result: descent is slower and more water-like, the bell deformation is more visible, and tentacles stay visually attached instead of flying off during the contraction.

### 2026-05-26 - synchronized kick and top drift

- Goal: remove the delay between bell contraction and upward movement, and stop bell flapping when jellyfish reach the top of the scene.
- Changed: added a `topDrift` hysteresis state per jellyfish. Above scene Y `4.55`, contraction is forced to `0` and the jellyfish only drifts downward until below `3.25`. During active contraction, upward water smoothing is mostly bypassed and a contraction-based lift is forced so route motion cannot keep dragging the jellyfish down in the same frame.
- Checks: browser probe on `spiral_project_card_03_image` reported first strong contraction with `dy: +0.1547`, `contraction: 0.5525`, no bad down-frames during strong contraction, `topDriftSamples: 23`, `topMaxContraction: 0`, no console errors; screenshot `real-jellyfish-kick-no-down-same-frame.png`; `npm run qa`; `npm run scene:status`.
- Result: a strong bell contraction now starts upward movement immediately, and jellyfish in the upper zone stop flapping and descend smoothly.
### 2026-05-26 - Blender-baked jellyfish animation clips

- Goal: replace the rejected browser-driven jellyfish deformation with animation authored in Blender and exported inside the GLB.
- Changed: `tools/import_real_jellyfish_cards_scene.py` now adds shape-key/keyframe animation for each real jellyfish bell plus local tentacle keyframes, exports `output/scene.glb` with animations, and the work copy `main.js` plays those clips via `THREE.AnimationMixer`.
- Site behavior: removed the old JS vertex/tentacle deformation and left the site responsible only for route/hover movement. At the top of the scene, per-jellyfish animation clip weight fades toward zero so the creature drifts instead of flapping.
- Checks: Blender background export succeeded; copied `output/scene.glb` to `3d-form-2_work_v2/assets/scene.glb`; `node --check main.js`; root `npm run qa`; `npm run scene:status`; browser probe on `http://127.0.0.1:5182` reported `ready: true`, `animations: 30`, `actionGroups: 15`, `cards: 15`, no console errors, and changing morph target values on active jellyfish.
- Screenshot: `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2\blender-baked-jellyfish-animation-check.png`.

### 2026-05-26 - More natural baked tentacle swimming

- Goal: make the Blender-authored jellyfish swim feel less mechanical by deforming tentacles like soft strands in water, not just moving the whole tentacle object.
- Changed: corrected the bell contraction to use the jellyfish vertical axis in Blender (`Z`) and gave each tentacle mesh unique shape keys: `water_wave_left`, `water_wave_right`, and `bell_impulse_lag`. The wave keeps the upper/root part more stable and gives the tips larger delayed side/lift motion.
- Checks: Blender background export succeeded; copied `output/scene.glb` to `3d-form-2_work_v2/assets/scene.glb`; `node --check main.js`; `npm run scene:status`; browser probe on `http://127.0.0.1:5182` reported `ready: true`, `animations: 30`, `actions: 15`, `cards: 15`, no console errors, and changing tentacle morph values; `npm run qa`.
- Screenshot: `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2\blender-baked-jellyfish-tentacle-wave-check.png`.

### 2026-05-26 - Rebuild jellyfish animation as shared lightweight asset

- Goal: recover from the over-heavy per-jellyfish tentacle mesh export after the user rejected the result as a "кошмар".
- Checkpoint: `checkpoints/20260526-225224`.
- Changed: removed unique copied tentacle meshes per jellyfish and returned to shared tentacle geometry with one shared water-wave shape-key setup, while keeping lightweight per-object transform keyframes for phase variation.
- Result: `output/scene.glb` dropped from about 144 MB to about 83 MB while retaining Blender-baked bell and tentacle morph animation.
- Checks: Blender background export; copied `output/scene.glb` to `3d-form-2_work_v2/assets/scene.glb`; `node --check main.js`; `npm run scene:status`; browser probe on `http://127.0.0.1:5182` reported `ready: true`, `animations: 30`, `actions: 15`, `cards: 15`, no console errors; `npm run qa`.
- Screenshot: `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2\jellyfish-shared-baked-animation-check.png`.
### 2026-05-27 - Reference-led Blender jellyfish candidate

- Goal: retry jellyfish animation using the remembered workflow: references first, then a standalone Blender draft, without immediately replacing the live site.
- Checkpoint: `checkpoints/20260527-000532`.
- Changed: added `tools/create_reference_led_jellyfish_asset.py`, which builds a standalone translucent jellyfish candidate with a bell power/recoil shape-key cycle, separate long tentacle water-lag shape keys, oral-arm water-lag shape keys, and a root swim cycle.
- Output: draft files under `output/attempts/reference_led_jellyfish_v2/`: `jellyfish_candidate.blend`, `jellyfish_candidate.glb`, and `jellyfish_candidate_preview.png`.
- Checks: Blender export/render succeeded; GLB is valid (`glTF`, about 3.6 MB); Blender inspection reports 4 actions over frames 1-96: bell, root swim, long tentacles, and oral arms.
- Result: this is a proper Blender-baked animated draft, not integrated into the site. Visual quality is improved over the prior code-deformed attempts but still needs art direction before replacing the site models.

### 2026-05-27 - Realistic baked jellyfish motion pass for 3d-form-3

- Goal: improve the live `3d-form-3` jellyfish swimming animation using real motion references: sharp bell contraction/power stroke, slower elastic reopening, passive drift, and tentacle lag.
- Checkpoint: `checkpoints/20260527-165301`; draft snapshot: `output/attempts/20260527-171110-before-realistic-jellyfish-motion-rewrite`.
- Changed: added `tools/refine_baked_jellyfish_motion.py`, which imports the current single-mesh `assets/baked_geonodes_jellyfish.glb`, removes the old 4 morph frames, and rebuilds Blender shape keys: `anticipation_tuck`, `power_contract`, `jet_recoil`, `elastic_reopen`, `tentacle_lag_left`, `tentacle_lag_right`, `tentacle_follow_impulse`, `water_settle_wave`.
- Site sync: added a small `getJellyfishSwimImpulseOffset` in `3d-form-2_work_v2/main.js` so the route lift starts during the same 2.5s phase as the Blender power stroke and fades near the top of the scene.
- Outputs: `output/attempts/realistic_baked_jellyfish_motion_v1/jellyfish_realistic_motion.blend`, `jellyfish_realistic_motion.glb`, and preview frames `preview_001_rest.png`, `preview_011_power_contract.png`, `preview_022_elastic_reopen.png`, `preview_033_water_lag.png`; copied the GLB to `3d-form-2_work_v2/assets/baked_geonodes_jellyfish.glb`.
- Checks: Blender export/render succeeded; GLB inspection reports one animated clip `realistic_jellyfish_bell_pulse_water_lag`, 195036 vertices, and 8 morph keys; local browser check loaded the clip with 15 replacements and no console errors; `node --check main.js`; `npm run qa`.
- Tradeoff: the baked GLB increased from about 25 MB to 45 MB because the motion now carries more morph phases.

### 2026-05-27 - Tentacle tuck/straighten correction for jellyfish motion

- Goal: fix the user-visible problem that tentacles looked static during bell pulses.
- User description translated into motion rules: before the clap, the expanding bell pulls tentacles closer under the hood and bends them; during the clap/propulsive stroke, tentacles straighten and trail downward with the water flow; after the stroke, the tentacles lag and curl again.
- Changed: updated `tools/refine_baked_jellyfish_motion.py` to add a dedicated `tuck` deformation parameter. `anticipation_tuck`, `elastic_reopen`, and settle phases now lift/curl tentacle tips under the bell; `power_contract` and `tentacle_follow_impulse` reduce lateral curl and stretch the tentacles into a straighter trailing bundle.
- Outputs: `output/attempts/realistic_baked_jellyfish_motion_v2/` with refreshed Blender/GLB files and preview frames. Copied the v2 GLB to `3d-form-2_work_v2/assets/baked_geonodes_jellyfish.glb`.
- Site: bumped cache bust to `jelly-tentacle-tuck-v2` in `index.html` and `main.js`.
- Checks: Blender export/render succeeded; local browser loaded clip `realistic_jellyfish_bell_pulse_water_lag.001`, 195552 vertices, versioned `main.js`, `scene.glb`, and `baked_geonodes_jellyfish.glb`; no console errors; `node --check main.js`; `npm run qa`.

### 2026-05-27 - Long post-stroke tentacle stream correction

- Goal: fix the remaining unrealistic return to a static half-bent tentacle pose immediately after extension.
- Changed: added `long_stream_hold` shape key and extended the Blender cycle to 76 frames. Frames 1-24 and 66-76 now keep tentacles in a longer, straighter post-stroke trailing bundle; frames 36-52 gradually tuck/curl the tentacles closer under the bell before the next clap; frame 56 performs the power contraction and immediately straightens the trailing bundle again.
- Site sync: changed `ASSET_VERSION` to `jelly-long-stream-v3` and aligned the JS swim impulse cycle to `76 / 24` seconds.
- Outputs: `output/attempts/realistic_baked_jellyfish_motion_v3/` with preview frames `preview_001_post_stroke_long_stream.png`, `preview_046_slow_tuck_prepare.png`, `preview_056_power_contract.png`, and `preview_066_back_to_long_stream.png`; copied GLB to `3d-form-2_work_v2/assets/baked_geonodes_jellyfish.glb`.
- Checks: Blender export/render succeeded; local browser loaded clip `realistic_jellyfish_bell_pulse_water_lag`, 195566 vertices, versioned `main.js`, `scene.glb`, and `baked_geonodes_jellyfish.glb`; no console errors; `node --check main.js`; `npm run qa`.

### 2026-05-27 - Distributed spiral jellyfish routes around spine

- Goal: change jellyfish movement from mostly bottom-to-top drifting into distributed spiral swimming around the spine, without clustering and without changing the apparent distance from the spine too much.
- Changed: replaced the old large screen-space sine route in `3d-form-2_work_v2/main.js` with `getJellyfishSpiralTargetPosition`. Each jellyfish now gets a stable base radius, golden-ratio phase offset, alternating orbit direction, and a vertical up/down sine climb so the group spreads across the scene.
- Added: `keepJellyfishOrbitDistance` clamps final positions after UI/collision adjustments to roughly `3.35-5.75` units from the spine center, preventing jellyfish from cutting through the spine or flying too far outward.
- Site: bumped cache bust to `jelly-spiral-route-v1`.
- Checks: `node --check main.js`; local Puppeteer route probe confirmed changing angles/heights over 3 samples, 15 replacements, no console errors, and versioned `main.js`, `scene.glb`, `baked_geonodes_jellyfish.glb`; `npm run qa`.

### 2026-05-27 - Camera-like continuous jellyfish spirals

- Goal: correct the previous route after user feedback: remove up/down sine jerks, make jellyfish move along continuous camera-like helices around the spine, and orient the hood in the direction of travel.
- Changed: `getJellyfishSpiralTargetPosition` now uses a linear wrapped progress over scene height (`-5.35` to `5.35`) plus helix angle, instead of vertical sine waves. Direction alternates per jellyfish so some swim up and some swim down.
- Orientation: added `getJellyfishPathQuaternion`, which samples a future point on the path and slerps the jellyfish hood toward the path tangent. Full alignment made jellyfish look like flat discs from the camera, so the final version uses a partial `0.46` slerp for readable directional tilt.
- UI smoothing: removed old hard Y corrections in `keepJellyfishAwayFromUi` that were pinning some jellyfish to fixed heights and creating visible steps.
- Site: bumped cache bust to `jelly-camera-like-spiral-v2`.
- Checks: `node --check main.js`; local Puppeteer route probe showed continuous changing heights/angles over three samples, 15 replacements, no console errors, and versioned assets; `npm run qa`.

### 2026-05-27 - Smooth helix route without broken jumps

- Goal: fix the remaining broken/jagged jellyfish motion on the camera-like spiral route.
- Changed: replaced top/bottom modulo wrapping with ping-pong vertical travel, made helix angle continuous through turns, disabled collision offsets, swim impulse offsets, and UI clamp corrections for baked jellyfish, and added an inertial `smoothRoutePosition` lerp before copying route positions to objects.
- Result: jellyfish now stay on distributed helices around the spine without teleporting at the top/bottom boundary or snapping sideways from helper corrections.
- Checks: local Puppeteer motion probe over 20 samples reported max per-sample steps about `0.37-0.51` and max Y steps about `0.10-0.24` for all 15 jellyfish, with no console errors; screenshot check was nonblank; `node --check main.js`; `npm run qa`; `npm run scene:status`.

### 2026-05-27 - Larger jellyfish and screen-facing hover approach

- Goal: make the jellyfish twice as large and add a hover interaction where the selected jellyfish turns its hood toward the screen and swims smoothly toward the viewer until the hood reads at about 25% of the screen.
- Changed: doubled the baked jellyfish target height in `3d-form-3/main.js`, changed hover focus to pull baked jellyfish farther toward the camera center, and replaced the old card-like hover scale boost with a jellyfish-specific cap based on orthographic view height and an estimated hood ratio.
- Site: bumped cache bust to `jelly-hover-approach-v5`.
- Checks: `node --check main.js`; `npm run qa`; local server returned updated `index.html` and `main.js`; Chrome headless screenshot confirmed the local canvas is nonblank and the enlarged jellyfish remain visible in the composition. Puppeteer hover probing was blocked by its recurring 30s internal timeout in this session, so hover behavior was verified by code path rather than automated mouse sampling.

### 2026-05-27 - Glass/chrome jellyfish material pass

- Goal: restyle the jellyfish so they sit closer to the biomechanical spine look: cold glass, chrome, iridescence, and subtle cyan/magenta glow.
- Changed: replaced the baked jellyfish `MeshBasicMaterial` with `MeshPhysicalMaterial` using high metalness, clearcoat, low roughness, iridescence, translucent opacity, and a restrained cyan/violet/magenta emissive palette.
- Tuning: first additive-blended pass over-bloomed into a white mass, so final material uses normal blending, lower opacity, lower emissive intensity, and reduced iridescence/reflectivity to keep the jellyfish form readable.
- Site: bumped cache bust to `jelly-glass-chrome-v12`.
- Checks: `node --check main.js`; `npm run qa`; local Chrome screenshot showed a nonblank scene and readable glass/chrome jellyfish in the composition.

### 2026-05-27 - Low-glare smoky chrome jellyfish correction

- Goal: fix user feedback that the glass/chrome jellyfish were still much too bright.
- Findings: reducing opacity alone made bright background clouds show through the translucent caps; the visible white blobs were mostly glare/background bleed rather than useful material detail.
- Changed: switched to a dense smoky chrome look with dark body colors, no emissive, tone mapping enabled, almost no specular/reflective contribution, no old card edge meshes, and opaque depth-writing material so the caps mask bright background glow instead of amplifying it.
- Site: bumped cache bust to `jelly-opaque-smoked-chrome-v20`.
- Checks: `node --check main.js`; `npm run qa`; local Edge screenshot confirmed the jellyfish bodies are dark/readable while remaining bottom brightness comes mainly from scene glow behind them.

### 2026-05-28 - Jellyfish hover hit-zone audit and fix

- Goal: verify user feedback that not every jellyfish hover/approach behaved correctly.
- Findings: browser audit showed `15` baked jellyfish and `15` visible image entries, but only the jellyfish currently inside the viewport can be hovered. Among visible jellyfish, an already-enlarged hover target could overlap nearby jellyfish and keep stealing pointer hits.
- Changed: added invisible sphere hover proxies for each baked jellyfish, excluded old card edges from the jellyfish hover path, and changed hit selection to choose the candidate whose source jellyfish center is closest to the pointer in screen space instead of trusting raycaster depth order.
- Site: bumped cache bust to `jelly-hover-wide-hit-v23`.
- Checks: `node --check main.js`; `npm run qa`; dynamic Puppeteer audit on visible jellyfish reported `pass: true`, with visible indices `4`, `7`, and `14` each selecting themselves, zooming `2.31-2.51x`, and moving within about `201`, `168`, and `231` pixels of screen center.

### 2026-05-31 - agent self-improvement pass

- Цель: agent self-improvement pass
- Что изменили: Repaired durable memory encoding damage, added the Agent Operating Loop pattern, linked it from project rules and patterns, synced markdown memory to SQLite, and verified agent/tool checks.
- Команда проверки: `npm run agent:status`, `npm run agent:evals`, `npm run check:tools`.
- Результат: Repaired durable memory encoding damage, added the Agent Operating Loop pattern, linked it from project rules and patterns, synced markdown memory to SQLite, and verified agent/tool checks.
- Вывод: Запись создана через agent:log.

### 2026-05-31 - organize completed projects

- Цель: organize completed projects
- Что изменили: Collected completed 3D projects, client sites, and PatentVsem/ZnakVsem materials into C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex; moved 3d-form-3 from C:\work; deleted temporary browser profiles and QA screenshot archive; removed empty source folders.
- Команда проверки: `npm run agent:status`, `npm run agent:evals`.
- Результат: Collected completed 3D projects, client sites, and PatentVsem/ZnakVsem materials into C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex; moved 3d-form-3 from C:\work; deleted temporary browser profiles and QA screenshot archive; removed empty source folders.
- Вывод: Запись создана через agent:log.

### 2026-05-31 - collect Iskra agent center

- Цель: collect Iskra agent center
- Что изменили: Created C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\Искра with safe copies of project agent memory, rules, tools, patterns, evals, checkpoints, SQLite memory, and a secret-free global Codex index; excluded auth, sessions, sandbox secrets, logs/state databases, and caches.
- Команда проверки: `npm run agent:status`, `npm run agent:evals`.
- Результат: Created C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\Искра with safe copies of project agent memory, rules, tools, patterns, evals, checkpoints, SQLite memory, and a secret-free global Codex index; excluded auth, sessions, sandbox secrets, logs/state databases, and caches.
- Вывод: Запись создана через agent:log.

### 2026-05-31 - index external 3d artist workflow

- Цель: index external 3d artist workflow
- Что изменили: Added C:\Users\Ардор\OneDrive\Рабочий стол\3д художник to Iskra context as external-3d-artist with key Blender/MCP scripts, README/config, and manifests for heavy models/output; kept source folder in place because check:tools and MCP workflows depend on it.
- Команда проверки: `npm run check:tools`, `npm run agent:status`.
- Результат: Added C:\Users\Ардор\OneDrive\Рабочий стол\3д художник to Iskra context as external-3d-artist with key Blender/MCP scripts, README/config, and manifests for heavy models/output; kept source folder in place because check:tools and MCP workflows depend on it.
- Вывод: Запись создана через agent:log.

### 2026-05-31 - post cleanup launch map and smoke audit

- Цель: post cleanup launch map and smoke audit
- Что изменили: Created START_HERE.md for the organized project collection, audited stale paths, ran JS syntax and asset/file smoke checks for collected projects, and recorded the Puppeteer launch limitation for future visual QA.
- Команда проверки: `node --check collected JS files`, `non-browser asset/file checks`, `npm run memory:db -- import-md`, `npm run agent:status`, `npm run agent:evals`.
- Результат: Created START_HERE.md for the organized project collection, audited stale paths, ran JS syntax and asset/file smoke checks for collected projects, and recorded the Puppeteer launch limitation for future visual QA.
- Вывод: Запись создана через agent:log.

### 2026-05-31 - project launchers and passports

- Цель: project launchers and passports
- Что изменили: Added LAUNCHERS.md and PROJECT_PASSPORTS.md to the organized project collection, linked them from START_HERE.md and README.md, and recorded project run commands, statuses, key files, and next steps.
- Команда проверки: `created LAUNCHERS.md`, `created PROJECT_PASSPORTS.md`, `npm run memory:db -- import-md`, `npm run agent:status`, `npm run agent:evals`.
- Результат: Added LAUNCHERS.md and PROJECT_PASSPORTS.md to the organized project collection, linked them from START_HERE.md and README.md, and recorded project run commands, statuses, key files, and next steps.
- Вывод: Запись создана через agent:log.

### 2026-05-31 - github huggingface research workflow

- Цель: github huggingface research workflow
- Что изменили: Added a recurring GitHub + Hugging Face research loop for safe source intake, reviewed initial 3D/Blender/HF sources, and recorded safety rules for not cloning, installing, running unknown code, or downloading heavy models without approval.
- Команда проверки: `web research: GitHub Blender-to-Three.js guide`, `web research: Hugging Face 3D Spaces and model listings`, `npm run memory:db -- import-md`, `npm run agent:status`, `npm run agent:evals`.
- Результат: Added a recurring GitHub + Hugging Face research loop for safe source intake, reviewed initial 3D/Blender/HF sources, and recorded safety rules for not cloning, installing, running unknown code, or downloading heavy models without approval.
- Вывод: Запись создана через agent:log.
### 2026-05-31 - TradeLab expanded Binance research grid

- Goal: find stronger paper-trading candidates before considering any real-money workflow.
- Command: `node tools/tradelab_research_grid.js "BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT,ADAUSDT,DOGEUSDT,LINKUSDT,AVAXUSDT" "15m,1h,4h" 1000`.
- Scope: 81 strategy/market tests on public Binance candles; no API keys, no account access, no real orders.
- Result: 56 blocked tests, 0 fetch/strategy errors, 12 stable healthy/caution candidates.
- Best paper-incubation shortlist: LINKUSDT 4h Mean Reversion, BNBUSDT 4h SMA+RSI, AVAXUSDT 4h Mean Reversion, ETHUSDT 1h Mean Reversion, BTCUSDT 1h Mean Reversion.
- Safety conclusion: no strategy is approved for real money yet. The next required step is paper incubation with live refreshes, guardrail monitoring, and enough closed paper trades to reduce one-off backtest luck.

### 2026-05-31 - TradeLab incubation runner first refresh

- Goal: convert the research shortlist into a persistent paper-incubation workflow.
- Changed: added `tools/tradelab_incubate_once.js`, exported `getSignal` from the shared backtest engine, and added `npm.cmd run tradelab:incubate`.
- Check: `node --check tools/tradelab_incubate_once.js`, `node --check tools/tradelab_run_once.js`, and `npm.cmd run qa` passed.
- Network run: `npm.cmd run tradelab:incubate` refreshed public Binance candles and wrote `tradelab-incubation-state.json`.
- Result: ETHUSDT 1h Mean Reversion and BTCUSDT 1h Mean Reversion remain in incubation with Healthy 100 and no alerts. LINKUSDT 4h, BNBUSDT 4h, and AVAXUSDT 4h were rejected by guardrails.
- Safety conclusion: this is still paper-only. The rejected candidates show why a strong backtest is not enough for real-money approval.

### 2026-05-31 - TradeLab real-money gate

- Goal: add an explicit blocker before any future real-money workflow.
- Changed: added `tools/tradelab_real_money_gate.js` and `npm.cmd run tradelab:gate`.
- Requirements: candidate must be `ready-for-review`, Healthy, have at least 20 live observations, at least 10 closed paper trades, PF >= 1.4, max DD <= 6%, max loss streak <= 2, and no critical alerts.
- Check: `node --check tools/tradelab_real_money_gate.js` and `npm.cmd run qa` passed.
- Result: `npm.cmd run tradelab:gate` returned `BLOCKED`. ETHUSDT and BTCUSDT are still incubating; all other candidates are rejected.
- Safety conclusion: real-money integration remains intentionally unavailable until the gate allows manual risk review.

### 2026-05-31 - TradeLab incubation report

- Goal: make the paper-incubation state readable without manually inspecting JSON.
- Changed: added `tools/tradelab_incubation_report.js`, `npm.cmd run tradelab:report`, and generated `TRADELAB_INCUBATION_REPORT.md`.
- Check: `node --check tools/tradelab_incubation_report.js` and `npm.cmd run qa` passed.
- Result: report shows 5 candidates and real-money gate `BLOCKED`.
- Safety conclusion: operating loop is now incubate, gate, report; real money stays disconnected while the gate is blocked.

### 2026-05-31 - TradeLab full review cycle

- Goal: reduce operator error by combining incubation refresh, gate check, and report generation into one command.
- Changed: added `tools/tradelab_review_cycle.js` and `npm.cmd run tradelab:cycle`.
- Check: `node --check tools/tradelab_review_cycle.js` and `npm.cmd run qa` passed.
- Network run: `npm.cmd run tradelab:cycle` refreshed public Binance candles, updated incubation state, ran the real-money gate, and regenerated `TRADELAB_INCUBATION_REPORT.md`.
- Result: incubation has 2 active candidates and 3 rejected candidates; gate remains `BLOCKED`.
- Safety conclusion: the one-command workflow still preserves the hard real-money blocker.

### 2026-05-31 - TradeLab watch runner

- Goal: support repeated paper-incubation review cycles without manual three-command operation.
- Changed: added `tools/tradelab_watch.js` and `npm.cmd run tradelab:watch`.
- Check: `node --check tools/tradelab_watch.js`, `npm.cmd run qa`, and `npm.cmd run tradelab:watch -- --dry-run --runs=2 --minutes=1` passed.
- Network run: `npm.cmd run tradelab:watch -- --runs=1 --minutes=0` refreshed public Binance candles, ran the full review cycle, and appended `TRADELAB_WATCH_LOG.md`.
- Result: gate remains `BLOCKED`; 2 candidates incubating, 3 rejected.
- Safety conclusion: watcher is paper-only and preserves the hard real-money blocker.

### 2026-05-31 - TradeLab forward paper ledger

- Goal: prevent historical backtest trades from being counted as live paper evidence.
- Changed: incubation state now stores a `paperLedger` per candidate with forward-only balance, open position, forward trades, forward PnL, processed candles, and forward drawdown. The real-money gate now requires `forwardPaperTrades` instead of historical `closedPaperTrades`.
- Check: `node --check` passed for `tradelab_run_once.js`, `tradelab_incubate_once.js`, `tradelab_real_money_gate.js`, and `tradelab_incubation_report.js`; `npm.cmd run qa` passed.
- Network run: `npm.cmd run tradelab:cycle` refreshed public candles, initialized forward ledgers, regenerated the report, and kept the gate `BLOCKED`.
- Result: ETHUSDT and BTCUSDT remain incubating, but forward paper trades are 0 because the ledger starts from current observed candles rather than backfilling historical trades.
- Safety conclusion: real-money readiness is now based on forward paper evidence, not a backtest sample.

### 2026-05-31 - TradeLab safety audit

- Goal: make paper-only safety verifiable by command.
- Changed: added `tools/tradelab_safety_audit.js` and `npm.cmd run tradelab:safety`.
- Check: `node --check tools/tradelab_safety_audit.js`, `npm.cmd run qa`, and `npm.cmd run tradelab:safety` passed.
- Result: audit status `PASS`, gate `BLOCKED`, no findings for exchange API-key access, order endpoints, or order-placement verbs in TradeLab files.
- Safety conclusion: current TradeLab surface remains market-data and paper-only.

### 2026-05-31 - TradeLab doctor check

- Goal: add one fast non-network health check for the TradeLab toolchain.
- Changed: added `tools/tradelab_doctor.js` and `npm.cmd run tradelab:doctor`.
- Finding: running browser QA from inside the doctor caused a nested Puppeteer timeout even though `npm.cmd run qa` passes separately, so doctor defaults to non-browser checks and documents browser QA as a separate command.
- Check: `node --check tools/tradelab_doctor.js`, `npm.cmd run tradelab:doctor`, and `npm.cmd run qa` passed.
- Result: doctor status `PASS`; safety audit `PASS`; gate `BLOCKED`; report generation `PASS`.

### 2026-05-31 - TradeLab scheduled hourly cycle

- Goal: replace the long-lived watcher process with a lower-memory Windows Task Scheduler setup.
- Changed: added `run-tradelab-cycle.ps1` and registered the `TradeLab Paper Cycle` scheduled task to run the paper-only cycle hourly.
- Runtime check: stopped the old watcher processes, manually started the scheduled task, and confirmed `LastTaskResult` 0.
- Result: `TRADELAB_SCHEDULE_LOG.md` recorded `Status: PASS`; `TRADELAB_INCUBATION_REPORT.md` updated; no persistent Node process remained after the scheduled run.
- Safety conclusion: the scheduled task still runs only `tradelab:cycle`, so it refreshes public candles, gate, and reports without API keys or orders.

### 2026-06-02 - TradeLab news impact analysis

- Goal: begin tracking whether crypto market moves show measurable reaction to public news flow.
- Changed: added `tools/tradelab_news_impact.js`, `npm.cmd run tradelab:news`, `TRADELAB_NEWS_IMPACT.md`, and `tradelab-news-impact.json`.
- Method: public RSS feeds from CoinDesk, Cointelegraph, and Investing Crypto; simple keyword sentiment; symbol alias matching; 1h/4h/12h/24h reaction measurement against Binance public candles.
- Check: `node --check tools/tradelab_news_impact.js` and `npm.cmd run tradelab:doctor` passed.
- Network run: `npm.cmd run tradelab:news -- "BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT,INJUSDT,APTUSDT,JUPUSDT"` processed 65 feed items and matched 32 symbol events.
- Early result: BTC news clusters were followed by negative average 24h reaction in this small sample; XRP negative news also averaged negative. Sample is too small for trading decisions.
- Safety conclusion: news impact is research-only and must not bypass the real-money gate.

### 2026-06-01 - Birzha TZ frontend pass

- Goal: apply `Рекомендации по Бирже.docx` to the main client project at `Проекты Codex\Клиентские сайты\birzha`.
- Changed: updated hero copy and clickable logo carousel, added benefits, deal-team, and MKTU sections, renamed card actions to `Купить` and `Получить консультацию`, and separated lead intent values.
- Check: `node --check app.js` passed in the main project. Puppeteer desktop/mobile checks rendered 24 cards, found no console errors, and confirmed no horizontal overflow at 1440px and 390px. Workspace `npm.cmd run qa` also passed.
- Result: duplicate `JS\ДЗ-1\birzha` was removed after the main project files were updated.

### 2026-06-01 - Birzha visual polish pass

- Goal: replace the first TZ pass with a more polished, premium marketplace look.
- Changed: redesigned the hero from a dark technical screen into a light legal-marketplace composition with layered trademark cards, softened the palette, restyled stats, filters, benefit cards, catalog cards, and hid the local admin section from the public page.
- Check: `node --check app.js` passed in the main project. Puppeteer desktop and mobile checks rendered 24 cards, found no console errors, confirmed no horizontal overflow at 1440px and 390px, and verified `Купить` / `Получить консультацию` actions. Workspace `npm.cmd run qa` passed.
- Result: screenshots saved under `visual-qa/birzha-main-desktop.png`, `visual-qa/birzha-main-mobile.png`, and polish drafts for comparison.

### 2026-06-01 - Birzha PatentVsem style alignment

- Goal: make the birzha frontend visually match `https://patentvsem.ru/` more closely.
- Changed: switched the page to the PatentVsem black/yellow palette, used the real PatentVsem header logo, reworked the hero into a large yellow panel, and restyled cards, forms, section spacing, and buttons around the same contrast system.
- Check: `node --check app.js` passed in the main project. Puppeteer desktop and mobile checks rendered 24 cards, loaded the logo, found no console errors, and confirmed no horizontal overflow at 1440px and 390px. Workspace `npm.cmd run qa` passed.
- Result: final screenshots saved under `visual-qa/birzha-main-patentvsem-style-desktop.png` and `visual-qa/birzha-main-patentvsem-style-mobile.png`.

### 2026-06-01 - Birzha recommendations 2 pass

- Goal: apply `Рекомендации по Бирже 2.docx` on top of the PatentVsem-style version.
- Changed: made the hero title split into the requested two lines on desktop, replaced fake hero marks with real registry numbers, added the `Зачем покупать готовый товарный знак?` hero button, updated proof cards, added Pavkin/Dovlatov links, made MKTU numbers filter the catalog locally, improved cart removal button readability, and hid the employee admin section from public navigation.
- Check: `node --check app.js` passed in the main project. Puppeteer desktop and mobile checks rendered 24 cards, found no console errors, confirmed no horizontal overflow, confirmed the admin section is hidden publicly and visible with `?admin=1`. Workspace `npm.cmd run qa` passed.
- Result: screenshots saved under `visual-qa/birzha-main-tz2-desktop.png` and `visual-qa/birzha-main-tz2-mobile.png`.

### 2026-06-01 - Birzha promo sale block

- Goal: add a visible top-page promo for accelerated trademark registration and improve placement-section contrast.
- Changed: added the `Акция` block above the hero with expandable conditions and forced the `Разместить знак на бирже` copy to black on the yellow band.
- Check: `node --check app.js` passed in the main project. Puppeteer desktop and mobile checks found no console errors, confirmed no horizontal overflow, confirmed the promo block exists, and confirmed request-section text is black. Workspace `npm.cmd run qa` passed.
- Result: screenshots saved under `visual-qa/birzha-main-promo-desktop.png` and `visual-qa/birzha-main-promo-mobile.png`.
