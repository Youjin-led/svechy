# Tasks

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
- [ ] Create implementation checkpoint before changing the frontend surface.
- [ ] Inspect current PatentVsem handmade site files and decide whether to build ZnakVsem as a separate folder under `сайты Игорька/`.
- [ ] Pull the first 30 trademark entries from `https://patentvsem.ru/tovarniy-znak` as starter catalog data.
- [ ] Build MVP catalog: cards, MKTU filter, discount filter, business-type filter, search with RU/EN transliteration, pagination.
- [ ] Build favorite list without accounts, stored locally in the visitor browser.
- [ ] Build cart/lead questionnaire that sends selected trademark data back through the PatentVsem lead flow.
- [ ] Build "place trademark" request form for manual admin review.
- [ ] Build simple admin surface for staff-only add/edit/remove trademark entries.
- [ ] Run frontend QA after implementation.

## Active

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
