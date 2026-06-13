# Tasks

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
