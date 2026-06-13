# Visual QA Pipeline

Use after frontend/3D changes.

## Command

```bash
npm run visual:qa -- --url http://127.0.0.1:5178/ --steps 4
```

## What It Checks

- Scene readiness via `window.__SCENE_READY`.
- Console, page, shader, and WebGL errors.
- Multiple screenshots across scroll positions.
- Canvas presence and non-empty screenshot output.
- Report written to `visual-qa/report.json`.

## Notes

- Some WebGL/postprocessing scenes return black from `readPixels` in headless mode, so screenshot file weight is used as a fallback.
- The screenshot is the source of truth for user-visible result.
