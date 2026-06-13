# Project Rules

## Назначение

Проект собирает 3D-сцену через локальных агентов и внешний Blender/3D-artist контур. Основной результат лежит в `output/`: `scene.blend`, `scene.glb`, `preview.png`, `report.json`.

## Команды

- `npm start -- "<prompt>"` - создать 3D-сцену через основной Python-оркестратор.
- `npm run start:web` - запустить старый web-генератор/просмотр.
- `npm run preview` - поднять статический просмотрщик.
- `npm run check:tools` - проверить доступность Blender, Node, npm, Puppeteer, Three.js и внешнего 3D artist.
- `npm run qa` - smoke-проверка `index.html` через Puppeteer.
- `npm run agent:status` - проверить наличие агентской обвязки проекта.
- `npm run memory -- add "текст"` - добавить заметку в память.
- `npm run memory -- search "запрос"` - найти заметки в памяти.
- `npm run memory:db -- add "текст" --tag project` - добавить заметку в SQLite-память.
- `npm run memory:db -- search "запрос"` - найти заметки в SQLite-памяти.
- `npm run memory:db -- import-md` - импортировать bullet-заметки из `AGENT_MEMORY.md`.
- `npm run agent:context` - собрать быстрый снимок проекта, инструментов, QA, задач и памяти.
- `npm run agent:log -- --title "..." --summary "..." --check "npm run qa"` - записать итог задачи в SQLite и markdown-журналы.
- `npm run agent:checkpoint -- create "описание"` - создать checkpoint агентской памяти и правил.
- `npm run agent:checkpoint -- list` - посмотреть последние checkpoints.
- `npm run agent:evals` - проверить базовые правила, роли, память, инструменты и команды агента.
- `npm run memory:db -- touch <id>` - отметить запись памяти как полезную.
- `npm run memory:db -- prune-candidates` - показать кандидатов на архивирование без удаления.
- `npm run scene:status` - показать честный статус только финальной сцены из `output/`.
- `npm run scene:attempt -- snapshot "описание"` - сохранить текущие финальные артефакты как отдельный черновой attempt.
- `npm run scene:attempt -- list` - показать сохраненные attempts.
- Blender найден по пути `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`.

## Рабочие соглашения

- Предпочитай небольшие точечные изменения.
- Сохраняй артефакты генерации в `output/`.
- Не коммить и не редактируй `node_modules/`.
- Проверяй результат через существующие QA-скрипты перед финальным ответом.
- Не удаляй память автоматически: сначала показывай кандидатов на архивирование.
- Для рискованных задач сначала создавай checkpoint.
- `output/preview.png` является единственным preview текущей сцены. Все остальные рендеры считаются черновиками.
- Перед новым визуальным проходом сохраняй текущий результат в `output/attempts/`, если он может понадобиться для сравнения.
