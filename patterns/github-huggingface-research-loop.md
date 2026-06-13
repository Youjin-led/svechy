# GitHub + Hugging Face Research Loop

Use this loop when improving Iskra, 3D/frontend projects, Blender pipelines, model generation, QA, or local agent tooling from public sources.

## Goal

Learn from GitHub and Hugging Face without turning the workspace into a dependency dump.

## Inputs

- A concrete theme, such as `Three.js GLTF animation`, `Blender morph target export`, `Hugging Face image-to-3D`, `visual QA`, or `agent memory`.
- Current project constraints from `AGENT_MEMORY.md`, `TASKS.md`, and `PROJECT_PASSPORTS.md`.

## Source Order

1. Official docs and primary repos.
2. Actively maintained GitHub repos with clear README, issues, examples, and license.
3. Hugging Face model/Space pages with visible task tags, update dates, examples, and license.
4. Secondary blog/forum posts only as supporting context.

## Triage Checklist

- Is the source current enough for the project stack?
- Does it solve a problem we actually have?
- Is the license acceptable?
- Does it require network, accounts, GPU, or large downloads?
- Can the useful part be copied as a small pattern, note, or local script instead of installing the whole project?
- Does it need a visual/3D QA check before we trust it?

## Output Types

- Add durable lessons to `AGENT_MEMORY.md`.
- Add reusable methods to `patterns/`.
- Add lightweight scripts to `tools/` only when they reduce repeat work.
- Add evals/checklists when the lesson is about quality control.
- Add candidate assets/models to manifests, not by downloading heavy files automatically.

## Safety Rules

- Do not install dependencies, clone large repos, run unknown code, or download heavy models without explicit user approval.
- Prefer reading and summarizing over importing.
- Keep exact URLs and why they matter in `EXPERIMENTS.md`.
- For Hugging Face, distinguish model availability from production readiness; many 3D models generate static GLB/mesh prototypes, not rigged animation.
- For 3D assets, always record provenance and inspect output before integrating.

## First Useful Watchlist

- Blender to Three.js glTF export: NLA tracks, shape keys, morph target limitations, static animation tracks.
- Three.js GLTFLoader and AnimationMixer behavior with morph targets.
- Hugging Face image-to-3D/text-to-3D: Hunyuan3D, TRELLIS, TripoSR, Stable Fast 3D, InstantMesh, VGGT, ActionMesh.
- Visual QA: screenshot diff, nonblank canvas checks, console error capture.
- Agent workflows: local memory, checkpoints, evals, task logs, prompt/pattern libraries.

## Cadence

For a research pass:

1. Pick 1-3 topics.
2. Browse current sources.
3. Save only the distilled lesson and links.
4. Implement a small local improvement if it is clearly useful.
5. Run relevant agent checks.
