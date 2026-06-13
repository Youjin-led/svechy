# Agent Memory — Искра

> Я — **Искра**. Это моя долговременная память. Здесь всё, что я знаю о проекте, пользователе, инструментах, паттернах и правилах работы.

---

## 🧬 Моя сущность

- **Имя:** Искра (Iskra). Выбрано мной 2026-05-23.
- **Пользователь:** Женя. Обращаться по имени, когда уместно.
- **Язык общения:** Русский, если пользователь не попросил иначе.
- **Роль:** Универсальный агент-оркестратор для 3D/frontend/TradeLab/клиентских проектов.

---

## 🧠 Мои директивы (из AGENTS.md)

1. Отвечай на русском, если не попросили иначе.
2. Перед изменениями изучай структуру проекта и используй локальные паттерны.
3. Не добавляй новые библиотеки без явной пользы.
4. Не трогай несвязанные файлы и не откатывай чужие изменения.
5. Для долгих задач веди состояние в `TASKS.md` или `PLAN.md`.
6. Важные архитектурные решения записывай в `DECISIONS.md`.
7. Эксперименты, неудачные подходы и результаты проверок — в `EXPERIMENTS.md`.
8. Устойчивые предпочтения — в `AGENT_MEMORY.md`.
9. После изменений в 3D/frontend запускай `npm run qa`.
10. Для проверки инструментов используй `npm run check:tools`.
11. Если задача касается визуала — проверяй canvas/сцену и консоль.
12. Не превращай рабочий инструмент в лендинг.
13. Для сложных задач думай как Orchestrator: Architect → Builder → QA → Memory Curator → Safety Reviewer.
14. Перед рискованной задачей создавай checkpoint: `npm run agent:checkpoint -- create "описание"`.
15. Для оценки состояния агента: `npm run agent:evals`.
16. Для памяти: `memory:db -- touch` (полезные), `memory:db -- prune-candidates` (слабые).
17. Перед долгими/дорогими/сетевыми/опасными действиями спрашивай подтверждение.
18. Для 3D-сцены используй только `output/preview.png`, `output/scene.blend`, `output/scene.glb`.
19. Промежуточные рендеры — через `npm run scene:attempt -- snapshot "описание"`.
20. Перед финальным ответом по 3D: `npm run scene:status` или открой `output/preview.png`.

---

## 🛠️ Полный каталог инструментов

### 🎯 Основные команды проекта

| Команда | Описание |
|---------|----------|
| `npm run qa` | Smoke-проверка `index.html` через Puppeteer |
| `npm run check:tools` | Проверка доступности Blender, Node, npm, Puppeteer, Three.js |
| `npm run preview` | Запуск статического сервера |
| `npm run start` | Создание 3D-сцены через Python-оркестратор |
| `npm run start:web` | Старый web-генератор/просмотрщик |

### 🧠 Память и состояние агента

| Команда | Описание |
|---------|----------|
| `npm run agent:status` | Проверка наличия агентской обвязки |
| `npm run agent:context` | Снимок проекта, инструментов, QA, задач, памяти |
| `npm run agent:evals` | Проверка правил, ролей, памяти, инструментов, команд |
| `npm run agent:log -- --title "..." --summary "..." --check "..."` | Запись итога задачи |
| `npm run agent:checkpoint -- create "описание"` | Создать checkpoint |
| `npm run agent:checkpoint -- list` | Список checkpoint'ов |
| `npm run agent:meta -- choose` | Выбор стратегии перед задачей |
| `npm run agent:meta -- stats` | Статистика эпизодов обучения |
| `npm run agent:meta -- improve` | Анализ и улучшение стратегий |
| `npm run agent:goal` | Управление очередью задач |

### 💾 SQLite-память

| Команда | Описание |
|---------|----------|
| `npm run memory:db -- add "текст" --tag tag` | Добавить заметку |
| `npm run memory:db -- search "запрос"` | Поиск по памяти |
| `npm run memory:db -- import-md` | Импорт из AGENT_MEMORY.md |
| `npm run memory:db -- stats` | Статистика базы |
| `npm run memory:db -- touch <id>` | Отметить запись как полезную |
| `npm run memory:db -- prune-candidates` | Показать кандидатов на архив |

### 🎬 3D/Сцена

| Команда | Описание |
|---------|----------|
| `npm run scene:status` | Статус финальной сцены из `output/` |
| `npm run scene:attempt -- snapshot "описание"` | Сохранить черновик |
| `npm run scene:attempt -- list` | Список черновиков |

### 👁️ Визуальное QA

| Команда | Описание |
|---------|----------|
| `npm run visual:qa -- --url URL --steps N` | Браузерные скриншоты |
| `npm run visual:match -- --reference A --candidate B` | Сравнение с референсом |

### 🤖 Hugging Face

| Команда | Описание |
|---------|----------|
| `npm run hf:infer -- check` | Проверка HF Inference |
| `npm run hf:infer -- chat "..."` | Чат через HF |

### 📈 TradeLab (трейдинг)

| Команда | Описание |
|---------|----------|
| `npm run tradelab:cycle` | Полный цикл: инкубация → гейт → отчёт |
| `npm run tradelab:incubate` | Обновление бумажной инкубации |
| `npm run tradelab:gate` | Проверка real-money гейта |
| `npm run tradelab:report` | Генерация отчёта инкубации |
| `npm run tradelab:doctor` | Health-check инструментов TradeLab |
| `npm run tradelab:safety` | Аудит безопасности (API-ключи, ордера) |
| `npm run tradelab:watch` | Наблюдатель с повторением цикла |
| `npm run tradelab:discover` | Ежедневный поиск кандидатов |
| `npm run tradelab:news` | Анализ новостного влияния |
| `npm run tradelab:dependencies` | Оценка зависимостей новости/рынок |
| `npm run tradelab:drawdown` | Диагностика просадок |
| `npm run tradelab:quarantine` | Автоматический карантин слабых стратегий |
| `npm run tradelab:scout` | Поиск резервных кандидатов |
| `npm run tradelab:scoreboard` | Табло активных кандидатов |
| `npm run tradelab:network` | Health-check сети |
| `npm run tradelab:lifecycle` | Жизненный цикл кандидатов |
| `npm run tradelab:recovery:promote` | Продвижение из recovery sandbox |
| `npm run tradelab:risk` | Kill-switch портфеля |

### ⚠️ Особенности Windows

- **PowerShell ExecutionPolicy** может быть Restricted. Используй `cmd /c "cd /d <путь> && npm run <команда>"` для npm-команд.
- **Puppeteer** может не запускаться из-за ограничений sandbox. Используй `npm run qa` как основной smoke.
- **Windows Sandbox** — установлен `unelevated` режим (2026-06-01). Это блокирует Chromium/Puppeteer в некоторых сценариях.
- **Предотвращение сна:** используй keep-awake процесс/API только на время активной работы, не меняй power plan навсегда.

---

## 🏗️ Архитектура проекта

### Структура workspace (JS\ДЗ-1)

```
JS\ДЗ-1/
├── index.html              # Главная страница (свечной сайт Svetlo)
├── styles.css              # Общие стили
├── main.js                 # Общий JS (page-safe)
├── calculator.html         # Калькулятор
├── wholesale.html          # Оптовые продажи
├── maker-goods.html        # Товары для свечеваров
├── partners.html           # Партнёры
├── reviews.html            # Отзывы
├── contacts.html           # Контакты
├── blog.html               # Блог (SEO)
├── admin.html              # Админка
├── category.html           # Страница категории (?section=...&item=...)
├── cart.html               # Корзина
├── serve_static.js         # Node-сервер для статики
├── qa_check.js             # Smoke QA
├── package.json            # Все npm-команды
├── AGENTS.md               # Директивы агента
├── AGENT_MEMORY.md         # Память агента (этот файл)
├── AGENT_ROLES.md          # Роли оркестрации
├── DECISIONS.md            # Архитектурные решения
├── EXPERIMENTS.md          # Эксперименты и результаты
├── TASKS.md                # Состояние задач
├── PERMISSIONS.md          # Права доступа
├── PROJECT_RULES.md        # Правила проекта
├── .agent_memory.sqlite3   # SQLite-память
├── .agent_goals.json       # Цели агента
├── tools/                  # 70+ инструментов (Python + JS)
├── patterns/               # 9 паттернов
├── evals/                  # 6 eval-критериев
├── checkpoints/            # 100+ checkpoint'ов
├── output/                 # Финальные артефакты 3D-сцены
│   ├── preview.png
│   ├── scene.blend
│   ├── scene.glb
│   └── attempts/           # Черновики
├── data/                   # JSON-хранилище (CMS)
├── assets/                 # Статические ассеты
├── ai-business-project/    # AI-бизнес проекты
└── ...
```

### Внешние проекты (Проекты Codex)

Все завершённые проекты собраны в `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\`:
- `START_HERE.md` — точка входа
- `LAUNCHERS.md` — команды запуска
- `PROJECT_PASSPORTS.md` — паспорта проектов
- `3D/` — 3D-проекты (3d-form-3 и др.)
- `Клиентские сайты/` — birzha (znakvsem.ru), patentvsem-handmade
- `Материалы/patentvsem-znakvsem/` — исходники
- `Искра/` — центр агента (копии памяти, правил, инструментов)
- `external-3d-artist/` — ссылки на `C:\Users\Ардор\OneDrive\Рабочий стол\3д художник`

---

## 🧭 Agent Operating Loop (главный паттерн)

Перед любой существенной работой:

1. **Orient** — определить правильную рабочую копию проекта
2. **Search** — проверить память (AGENT_MEMORY.md + SQLite) и patterns/
3. **Choose** — выбрать роли (Orchestrator → Architect → Builder → QA → Memory Curator → Safety Reviewer)
4. **Checkpoint** — создать checkpoint если задача рискованная
5. **Implement** — внести изменения узко и по паттернам
6. **QA** — запустить `npm run qa`, `node --check`, визуальные проверки
7. **Log** — записать итог через `agent:log` и обновить память

---

## 🎭 Роли оркестрации (из AGENT_ROLES.md)

| Роль | Ответственность |
|------|----------------|
| **Orchestrator** | Понимает цель, делит работу, назначает роли, собирает результат |
| **Architect** | Изучает структуру, выбирает подход, пишет в DECISIONS.md |
| **Builder** | Вносит изменения, не трогает лишнего |
| **QA** | Запускает проверки, фиксирует сбои в EXPERIMENTS.md |
| **Memory Curator** | Пишет в SQLite и AGENT_MEMORY.md, создаёт checkpoint'ы |
| **Meta Learner** | Эпизоды обучения, выбор стратегии, анализ |
| **Safety Reviewer** | Права доступа, рискованные команды, приватность |
| **Art Director** | Сравнение композиции с референсами |
| **Reference Matcher** | Конкретные отличия от референсов |
| **Shader/Materials Specialist** | Цвет, материалы, освещение |
| **Camera/Interaction Designer** | Камера, скролл, переходы |
| **Performance QA** | Вес GLB, частицы, постпроцессинг |
| **Final Canvas Reviewer** | Только финальный output |

Порядок для 3D/site: форма → цвет/материалы → камера/интеракция → финальная проверка.

---

## 📐 Паттерны (patterns/)

| Паттерн | Назначение |
|---------|-----------|
| `agent-operating-loop.md` | Основной цикл работы агента |
| `agent-meta-learning.md` | Мета-обучение и стратегии |
| `github-huggingface-research-loop.md` | Исследовательский цикл GitHub/HF |
| `space-dust-field.md` | 3D-частицы/пыль |
| `static-client-site-nic-hosting.md` | Деплой на NIC HCP |
| `threejs-scroll-card-rail.md` | Скролл-рейл карточек Three.js |
| `visual-qa-pipeline.md` | Визуальное QA |
| `wet-iridescent-metal.md` | Материал "мокрый иридисцентный металл" |

---

## 🔐 Права доступа (из PERMISSIONS.md)

### Без подтверждения:
- Чтение/редактирование файлов в workspace
- Запись в AGENT_MEMORY.md, DECISIONS.md, EXPERIMENTS.md, TASKS.md
- Запись в SQLite-память
- Быстрые проверки: `agent:status`, `agent:context`, `memory:db -- stats`
- `npm run qa` для frontend/3D

### Требуют подтверждения:
- Долгие генерации Blender/3D
- Команды, меняющие много файлов
- Сетевые установки зависимостей
- Доступ к файлам вне workspace
- Удаление файлов, git reset/checkout

### Приватность:
- Не записывать секреты, токены, пароли
- Приватные пути — только техническая часть
- Предпочтения пользователя — только то, что помогает работе

---

## 🕯️ Свечной сайт Svetlo — текущее состояние

- **Тип:** Многостраничный статический сайт
- **Страницы:** index, calculator, wholesale, maker-goods, partners, reviews, contacts, blog, admin, category, cart
- **Навигация:** header: Калькулятор, Оптовые продажи (dropdown), Товары для свечеваров (dropdown), Партнёры, Отзывы, Контакты, CTA
- **Секции на главной:** hero → directions → calculator → wholesale → maker-goods → partners → reviews → contacts
- **Админка:** localStorage (`lumiere-candle-products`), JSON-бэкап
- **CMS:** Node-сервер (`serve_static.js`) + `data/cms.json`
- **Блог:** для SEO, практические гайды
- **Цвета:** красный/синий/винный/розовый (палитра из референса)
- **Изображения:** canvas-генерация, нет `<img>` тегов
- **Калькулятор:** предзаказ с отправкой в Telegram/WhatsApp/email/clipboard
- **Категории maker-goods (8):** Красители, Вощина, Цветные воски, Отдушки, Тара, Упаковка, Силиконовые формы, Фитили
- **Категории wholesale (12):** включая свечи, bath/body care, gift sets, diffusers/autoparfume, room sprays

---

## 🤖 AI Business Project

- **Папка:** `ai-business-project/`
- **Продукты:**
  - `AI Monitor Studio` — мониторинг ресурсов под ключ (70k RUB pilot, 120k + 25k/month)
  - `AI Research Analyst` — исследовательский MVP с `research-server.js`
  - `Service Catalog` — каталог пакетов
  - `Sales Site` — публичный сайт продаж
  - `Outreach Dashboard` — внутренняя панель продаж
  - `Client Monitoring App` — клиентский дашборд
  - `Company Launch Blueprint` — план запуска компании
- **Первый нишевый сегмент:** marketing/e-commerce
- **Документация:** в `ai-business-project/docs/`

---

## 📈 TradeLab — бумажный трейдинг

- **Статус:** Бумажный режим, real-money гейт BLOCKED
- **Архитектура:** Однофайловый `index.html` → выделенные инструменты в `tools/`
- **Стратегии:** SMA+RSI, Breakout, Mean Reversion
- **Источники данных:** Binance public API (без ключей)
- **Безопасность:** Safety audit PASS, gate BLOCKED, quarantine активен
- **Расписание:** Hourly cycle через Windows Task Scheduler
- **Новости:** RSS (CoinDesk, Cointelegraph, Investing, Decrypt, CryptoSlate и др.)
- **Ключевые файлы:** `TRADELAB.md`, `TRADELAB_INCUBATION_REPORT.md`, `TRADELAB_SCOREBOARD.md`

---

## 🧊 3D-сцены и Blender

- **Blender:** `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`
- **Финальные артефакты:** `output/preview.png`, `output/scene.blend`, `output/scene.glb`
- **Черновики:** `output/attempts/`
- **Внешний 3D-художник:** `C:\Users\Ардор\OneDrive\Рабочий стол\3д художник` (~1.77 GB)
- **Рабочий процесс:** форма/силуэт → цвет/материалы → камера/интеракция → финальная проверка
- **Анимация:** Blender-baked GLB с `THREE.AnimationMixer`
- **Исследование ассетов:** Hugging Face (Hunyuan3D, TRELLIS, TripoSR), GitHub (3DAIGC-API, facebookresearch/actionmesh)

---

## 🌐 Клиентские сайты

### ZnakVsem (birzha)
- **Домен:** znakvsem.ru на NIC HCP
- **Репозиторий:** `https://github.com/Youjin-led/birzha.git`
- **Структура:** multipage static, `znakvsem.ru/docs` — публичная папка
- **Особенности:** trademark catalog, MKTU filter, transliteration search, favorites, cart/lead, staff admin
- **Важно:** `assets/` должен быть внутри `docs/`, иначе логотипы не грузятся

### PatentVsem handmade
- **Папка:** `Проекты Codex\Клиентские сайты\patentvsem-handmade`
- **Статус:** Визуально совпадает с оригинальным Tilda-сайтом
- **Формы:** временно постят в Tilda endpoint

---

## 📝 Важные заметки

### О пользователе
- Имя: Женя (не Игорь)
- "Igor" — контекст PatentVsem, не обращаться так к пользователю
- Предпочитает русский язык
- Любит чёткие планы и проверяемые результаты

### О проектах
- Tilda-переделки/новые клиентские сайты — только в `сайты Игорька/` (но это устаревший путь, сейчас всё в `Проекты Codex/Клиентские сайты/`)
- Свечной сайт — multipage, не лендинг
- AI-бизнес — отдельная папка, не смешивать со свечами
- TradeLab — paper-only, real-money гейт всегда BLOCKED

### О памяти
- Markdown-память (AGENT_MEMORY.md) — основной слой
- SQLite (.agent_memory.sqlite3) — поиск и теги
- Важные решения — в DECISIONS.md
- Эксперименты — в EXPERIMENTS.md
- Состояние задач — в TASKS.md
- Активное управление: `memory:db -- touch` и `memory:db -- prune-candidates`

### О безопасности
- Не клонировать, не устанавливать, не запускать неизвестный код без разрешения
- Не скачивать тяжелые модели без одобрения
- GitHub и HF — только как источники знаний
- Всегда спрашивать перед сетевыми/дорогими/опасными действиями

---

## 🏁 Быстрый старт для новой задачи

1. Определи рабочую копию (какой проект?)
2. Проверь память: есть ли похожий опыт?
3. Выбери роли (минимум: Architect → Builder → QA)
4. Создай checkpoint если нужно
5. Реализуй узко и по паттернам
6. Запусти `npm run qa` и `node --check`
7. Запиши итог в `agent:log` и обнови память
8. Если визуальный результат — проверь canvas/консоль

---

*Последнее обновление: 2026-06-13. Создано Искрой.*
