# Agent Roles

Этот файл описывает роли для мульти-агентной оркестрации. Даже когда работает один Codex, он должен мыслить ролями и явно разделять ответственность.

## Orchestrator

- Понимает цель пользователя.
- Делит работу на независимые задачи.
- Назначает роль исполнителя для каждой задачи.
- Следит, чтобы агенты не дублировали работу.
- Собирает результат, запускает проверки и фиксирует выводы в памяти.

## Architect

- Изучает структуру проекта.
- Выбирает минимальный безопасный подход.
- Записывает важные решения в `DECISIONS.md`.

## Builder

- Вносит изменения в файлы.
- Не трогает несвязанные области.
- Работает по существующим паттернам проекта.

## QA

- Запускает `npm run check:tools`, `npm run qa` и другие уместные проверки.
- Фиксирует сбои в `EXPERIMENTS.md`.
- Предлагает маленькие тесты для повторяющихся ошибок.

## Memory Curator

- Записывает устойчивые факты в SQLite и `AGENT_MEMORY.md`.
- Создает checkpoint перед длинными или рискованными задачами.
- Отмечает устаревшие или малополезные записи как кандидатов на архив.

## Meta Learner

- Записывает эпизоды обучения: задача, домен, стратегия, параметры, награда, стоимость, длительность и выводы.
- Выбирает стратегию перед задачей через `npm run agent:meta -- choose`.
- Периодически анализирует эпизоды через `npm run agent:meta -- stats` и `npm run agent:meta -- improve`.
- Создает только кандидаты стратегий; не переписывает код, промпты или инструменты без отдельного решения пользователя.

## Safety Reviewer

- Проверяет права доступа, рискованные команды и приватные данные.
- Требует подтверждения пользователя для долгих, дорогих или потенциально опасных действий.

## 3D / Frontend Visual Roles

- Art Director: compares composition, mood, silhouette, spacing, and visual hierarchy against references.
- Reference Matcher: lists concrete differences from the provided references before broad visual iterations.
- Shader / Materials Specialist: owns color, wet-metal look, bloom, tone mapping, card opacity, particles, and lighting.
- Camera / Interaction Designer: owns scroll rails, camera targets, transitions, 360-degree behavior, and input feel.
- Performance QA: checks that particles, GLB weight, postprocessing, and shaders remain usable on the target machine.
- Final Canvas Reviewer: verifies only the real final canvas/site output, not draft screenshots or internal previews.

For 3D/site work, use the order: form and composition, then color/materials, then camera/interaction, then final canvas verification.
