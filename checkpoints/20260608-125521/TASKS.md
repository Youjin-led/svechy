# Tasks

## Active - AI business project

- [x] Create checkpoint before packaging the new business project.
- [x] Build standalone `ai-business-project/` folder with business plan, implementation playbook, sales playbook, governance notes, financial model, and static presentation page.
- [x] Run syntax, local QA, tool check, and Puppeteer desktop/mobile smoke for the new page.
- [x] Add `AI Research Analyst` MVP for internet information collection, source analysis, report generation, and research workflow packaging.
- [x] Upgrade `AI Research Analyst` with a local Node server for live web search, URL fetching, text extraction, source reliability scoring, and automatic source-card filling.
- [x] Package the market-facing offer as `AI Monitor Studio`: offer page, commercial proposal, demo report, sales script, target client list, and pricing/economics notes.

## Active - Candle site MVP

- [x] Create checkpoint before replacing the frontend surface.
- [x] Build a static candle atelier website in `index.html`, `styles.css`, and `main.js`.
- [x] Add first-screen candle canvas, responsive catalog, filters, set presets, cart drawer, and lead form.
- [x] Run `npm run check:tools`, `node --check main.js`, `npm run qa`, and desktop/mobile Puppeteer visual smoke.
- [x] Redesign candle site toward a simple Meliponini-like preorder flow with aesthetic color palette, calculator, and messenger/email order links.
- [x] Remove prefilled public cards and add a local admin surface for adding, editing, deleting, and saving cards in browser storage.
- [ ] Replace local canvas-generated product visuals with real product photography when brand assets are available.
- [ ] Replace placeholder email/domain with the real Telegram, WhatsApp, email, and optional CRM endpoint.

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
- [x] Add saved runs, report exports, risk metrics, chart trade markers, train/test shading, and strategy presets.
- [x] Add trading costs and direction modes: commission, slippage, long-only, short-only, and long+short.
- [x] Add portfolio mode with multi-CSV upload and per-symbol/aggregate results.
- [x] Add Binance public market-data fetch for candles without API keys or trading.
- [x] Add paper live loop that refreshes Binance candles, updates paper signals/actions, and writes a live log.
- [x] Add live guardrails and alerts with optional auto-entry blocking.
- [x] Add Strategy Health panel with score, status, reasons, and recommendation.
- [x] Run Binance research grid across BTC/ETH/SOL and 15m/1h/4h/1d to identify paper-live candidates.
- [x] Add browser Research Grid panel and Research Results table for Binance walk-forward scans.
- [x] Add Candidate Watchlist with add/apply/live/delete actions.
- [x] Add candidate incubation lifecycle and final readiness documentation.
- [x] Run expanded Binance research grid across 9 symbols and 15m/1h/4h to produce a paper-incubation shortlist.
- [x] Add persistent TradeLab incubation runner and run the first guardrail refresh.
- [x] Add real-money readiness gate that blocks every candidate until paper-incubation requirements are met.
- [x] Add readable incubation report generator for operator review.
- [x] Add one-command TradeLab review cycle: incubation, gate, and report.
- [x] Add repeated paper watch runner with Markdown log.
- [x] Add forward-only paper ledger so real-money gate does not count historical backtest trades as live evidence.
- [x] Add TradeLab safety audit for API-key/order-endpoint checks and gate verification.
- [x] Add TradeLab doctor command for fast non-network health checks.
- [x] Start a 24-hour paper watch run for autonomous hourly TradeLab monitoring.
- [x] Replace long-lived watcher with Windows Task Scheduler hourly paper cycle.
- [x] Run expanded zero-money research across 20 symbols and add stronger candidates to paper incubation.
- [x] Add daily discovery job that can automatically add strict zero-money candidates to paper incubation.
- [x] Add news-impact research layer for public RSS sentiment and post-news candle reactions.
- [x] Schedule news-impact analysis twice daily.
- [x] Add news/market dependency scoring from news-impact events.
- [x] Expand news-impact sources and tracked symbol coverage.
- [x] Add TradeLab drawdown diagnostics by symbol, timeframe, strategy, exit reason, and news context.
- [x] Add automatic quarantine for weak TradeLab symbols, strategies, and candidates.
- [ ] Incubate shortlisted candidates in paper mode until each has enough live paper observations and no critical guardrail alerts.

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
