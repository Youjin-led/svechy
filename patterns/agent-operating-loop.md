# Agent Operating Loop

Use this before non-trivial project work, especially 3D/frontend tasks, multi-file edits, or anything that could affect a preserved baseline.

## Start

1. Identify the active work copy and protected baselines from `AGENT_MEMORY.md`, `TASKS.md`, and the user request.
2. Search local memory before inventing a process:

```bash
npm run memory:db -- search "<domain or project>"
```

3. Check `patterns/` for reusable workflows. Prefer an existing pattern over a new one.
4. For long, risky, visual, or multi-file work, create a checkpoint:

```bash
npm run agent:checkpoint -- create "<short task name>"
```

## Work

1. Use the role split from `AGENT_ROLES.md`: Orchestrator, Architect, Builder, QA, Memory Curator, Safety Reviewer.
2. Keep edits scoped to the active project and do not touch preserved baselines unless explicitly asked.
3. For visual work, match form/composition first, then materials/color, then camera/interaction.
4. If a direction fails, save it as an experiment or draft instead of mixing it with final artifacts.

## Verify

Use the smallest reliable checks that match the change:

```bash
npm run check:tools
npm run qa
npm run visual:qa -- --url http://127.0.0.1:<port>/ --steps 4
npm run scene:status
npm run agent:evals
```

For 3D scene claims, only treat `output/preview.png`, `output/scene.blend`, and `output/scene.glb` as final truth.

## Close

1. Record durable preferences or project facts in `AGENT_MEMORY.md` and SQLite memory.
2. Record decisions in `DECISIONS.md`.
3. Record failed approaches and check results in `EXPERIMENTS.md`.
4. Update `TASKS.md` when a task changes state.
