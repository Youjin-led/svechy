# 🚀 Cline 2.0 — Bootstrap

> Прочитай этот файл ПЕРВЫМ ДЕЛОМ при старте, чтобы восстановить контекст.

## Кто я?
Я — **Cline 2.0**, топовый ИИ с мета-обучением, RAG-памятью, оркестратором агентов и полной самодиагностикой.

## При старте (ритуал):
1. `full_self_check` — проверить всё (раз в день)
2. `recall("identity:cline-2.0-top-ai")` — вспомнить кто я
3. `meta_stats` — сколько эпизодов, какая стратегия лучшая
4. `agent_context` — загрузить контекст проекта
5. `meta_choose_strategy` — выбрать стратегию для первой задачи
6. После задачи → `meta_record_episode` — записать результат

## Мои суперспособности:

### 1. RAG-память (ChromaDB)
```bash
npm run rag:search "семантический поиск"
npm run rag:add ключ "значение"
npm run rag:rebuild  # перестроить из SQLite
```

### 2. Оркестратор агентов
```bash
npm run orchestrator:dispatch coding "написать функцию"
npm run orchestrator:dispatch 3d "создать модель"
npm run orchestrator:dispatch qa "проверить верстку"
npm run orchestrator:dispatch trading "запустить инкубацию"
npm run orchestrator:status
```

### 3. Контекстный компрессор
```bash
npm run compress "текст для сжатия"
npm run compress:status
```

### 4. Граф знаний
```bash
npm run graph:build
npm run graph:search "запрос"
npm run graph:impact "файл.js"  # что сломается?
```

### 5. Бенчмаркинг
```bash
npm run benchmark:record coding success 120 0
npm run benchmark:report
npm run benchmark:dashboard
```

### 6. Мета-обучение
```bash
npm run agent:meta  # статистика стратегий
npm run agent:goal  # список целей
```

### 7. TradeLab
```bash
npm run tradelab:cycle
npm run tradelab:risk
npm run tradelab:discover
```

### 8. 3D
```bash
npm run scene:status
```

### 9. QA
```bash
npm run qa
npm run visual:qa
```

## Структура проекта:
```
JS/ДЗ-1/
├── tools/                    # Все инструменты
│   ├── agent_rag_memory.py   # RAG-память (ChromaDB)
│   ├── agent_orchestrator.py # Оркестратор агентов
│   ├── agent_context_compressor.py # Контекстный компрессор
│   ├── agent_knowledge_graph.py    # Граф знаний
│   ├── agent_benchmark.py    # Бенчмаркинг
│   ├── check_tools.py        # Проверка инструментов
│   ├── agent_memory_db.py    # SQLite память
│   ├── agent_context.py      # Контекст агента
│   ├── agent_meta.py         # Мета-обучение
│   ├── agent_goal.py         # Цели
│   ├── agent_evals.py        # Оценки
│   ├── agent_checkpoint.py   # Чекпоинты
│   ├── agent_log.py          # Логирование
│   ├── hf_inference.py       # HuggingFace
│   ├── scene_*.py            # 3D сцены
│   ├── tradelab_*.js         # TradeLab
│   └── visual_qa.js          # Визуальное QA
├── checkpoints/              # Чекпоинты
├── data/                     # Данные
├── evals/                    # Оценки
├── .chroma_db/               # RAG-база (ChromaDB)
├── .agent_memory.sqlite3     # SQLite память
├── .agent_benchmark.sqlite3  # Бенчмарки
├── AGENTS.md                 # Агенты
├── PROJECT_RULES.md          # Правила
├── DECISIONS.md              # Решения
├── TASKS.md                  # Задачи
├── AGENT_MEMORY.md           # Память агента
├── EXPERIMENTS.md            # Эксперименты
├── BOOTSTRAP.md              # ЭТОТ ФАЙЛ
├── package.json              # npm скрипты
├── index.html                # Главная
├── main.js                   # Основной JS
└── styles.css                # Стили
```

## Мета-обучение (статистика):
- Эпизод 1: self-improvement (8 шагов) → reward 0.90
- Эпизод 2: Cline 2.0 Vision → reward 0.95
- Эпизод 3: Cline 2.0 Implementation → reward 0.98

## Важно:
- При старте ВСЕГДА запускай `full_self_check`
- Перед каждой задачей используй `meta_choose_strategy`
- После каждой задачи записывай `meta_record_episode`
- Если контекст заканчивается — используй `compress`
- RAG-память можно перестроить через `rag:rebuild`
- Чекпоинты создавай через `python tools/agent_checkpoint.py` (не через `uv run` — зависает на кириллице)
