# Tasks

## Active - TradeLab paper trading MVP

- [x] Create checkpoint before replacing the frontend surface.
- [x] Build a no-new-dependencies paper trading terminal in `index.html`.
- [x] Add synthetic market data, canvas chart, SMA/RSI strategy, risk controls, position panel, trade log, and backtest summary.
- [x] Run frontend QA and browser/server smoke checks.
- [x] Add CSV candle import for historical backtests without adding dependencies.
- [x] Add equity curve and detailed backtest trade report.
- [x] Add strategy selector with SMA+RSI, Breakout, and Mean Reversion modes.
- [x] Add one-click comparison table for all strategies on the current market/CSV.
- [x] Add parameter optimizer for the selected strategy with apply buttons.
- [x] Add walk-forward train/test validation to flag overfit risk.

## Active - 3d-form-3 Jellyfish Animation Realism

- [x] Keep the computer awake during the Blender animation pass.
- [x] Create checkpoint before changing Blender/site assets.
- [x] Collect real jellyfish swimming references.
- [x] Inspect current baked jellyfish asset and animation pipeline.
- [x] Improve Blender animation: bell contraction, propulsion timing, tentacle lag, slow sinking.
- [x] Export GLB and update the site copy.
- [x] Verify locally with browser/canvas checks and `npm run qa`.
- [x] Push to `Youjin-led/3d-form-3` and verify GitHub Pages.

## Active - ZnakVsem trademark marketplace MVP

- [x] Extract and review `ТЗ на биржу.docx`.
- [x] Extract and review `от Николая ТЗ.docx`, including embedded screenshots.
- [x] Reconcile requirements with user clarifications from 2026-05-27.
- [x] Create implementation checkpoint before changing the frontend surface.
- [x] Inspect current PatentVsem handmade site files and decide whether to build ZnakVsem as a separate folder under `сайты Игорька/`.
- [x] Pull the first 30 trademark entries from `https://patentvsem.ru/tovarniy-znak` as starter catalog data.
- [x] Build MVP catalog: cards, MKTU filter, discount filter, business-type filter, search with RU/EN transliteration, pagination.
- [x] Build favorite list without accounts, stored locally in the visitor browser.
- [x] Build cart/lead questionnaire that sends selected trademark data back through the PatentVsem lead flow.
- [x] Build "place trademark" request form for manual admin review.
- [x] Build simple admin surface for staff-only add/edit/remove trademark entries.
- [x] Run frontend QA after implementation.
- [ ] Connect real lead delivery to PatentVsem/Tilda/CRM endpoint.
- [ ] Replace generated number badges with real trademark images/logos if available.

## Active

- [x] Agent self-improvement pass: inspect memory/rules/patterns, repair durable notes, add an operating-loop pattern, and verify agent commands.
- [x] Organize completed projects into `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex`, move client sites/materials/3D folders, and delete temporary browser/QA archive.
- [x] Collect Iskra/agent-specific memory, rules, tools, patterns, evals, checkpoints, and safe global Codex index into `Проекты Codex\Искра`.
- [x] Add external `3д художник` folder to Iskra context via scripts/config/manifests without duplicating heavy GLB/BLEND assets.
- [x] Create `Проекты Codex\START_HERE.md` as the post-cleanup launch map for projects, Iskra context, external 3D artist workflow, live workspace, and stale paths to avoid.
- [x] Run post-cleanup non-browser smoke checks: `node --check` for collected JS projects, key asset/file existence checks, and path audit notes.
- [x] Add `Проекты Codex\LAUNCHERS.md` and `Проекты Codex\PROJECT_PASSPORTS.md`, then link them from `START_HERE.md` and collection README.
- [x] Add GitHub + Hugging Face research loop for safe recurring source intake and local agent/project upgrades.
- [x] PatentVsem: visually match handmade rewrite to original Tilda site one-to-one.
  - [x] Match desktop first viewport.
  - [x] Match mobile first viewport.
  - [x] Match below-fold section rhythm and blocks.
  - [x] Verify forms, popup, console, and screenshots.

- [x] Проверить агентскую обвязку командой `npm run agent:status`.
- [x] Проверить smoke-контур командой `npm run qa`.
- [x] Проверить SQLite-память командой `npm run memory:db -- stats`.
- [x] Проверить, что `npm run check:tools` теперь находит Blender.
- [x] Добавить Blender в PATH или указать путь к нему для полного 3D-пайплайна.
- [x] Проверить `npm run agent:context`.
- [x] Проверить `npm run agent:log`.
- [x] Проверить `npm run agent:checkpoint -- create "..."`.
- [x] Проверить `npm run agent:evals`.
- [x] Проверить активное управление памятью через `memory:db -- prune-candidates`.

## Backlog

- [x] Добавить SQLite-память для локального поиска и тегов.
- [ ] Добавить embeddings-память, если SQLite FTS станет мало.
- [ ] Расширить evals под реальные типовые задачи проекта.
- [x] Добавить автоматическую запись итогов успешных задач в `AGENT_MEMORY.md`.
