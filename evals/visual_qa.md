# Visual QA Eval

## Goal

Check that visual/frontend work is verified against the real browser canvas, not only against internal screenshots or assumptions.

## Criteria

- `visual:qa` opens the site in Chromium.
- It waits until `window.__SCENE_READY` or `window.__SCENE_ERROR`.
- It captures multiple frames, including scroll positions when the scene supports scroll navigation.
- It records console, WebGL, and shader errors.
- It samples canvas pixels and fails when the canvas is missing or effectively blank.
- It writes `visual-qa/report.json` plus frame screenshots.

## Commands

- `npm run visual:qa -- --url http://127.0.0.1:5178/ --steps 4`
- `npm run visual:qa -- --url http://127.0.0.1:5178/ --steps 2 --mobile`
