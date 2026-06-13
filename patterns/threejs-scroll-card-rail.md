# Three.js Scroll Card Rail

Use when a 3D scene has a vertical/spiral stack of project cards and scroll should move from one featured card to the next.

## Shape

- Extract real world centers from named meshes such as `spiral_project_card_00_image`.
- Sort stops by card index or world Y, depending on the art direction.
- Disable free `OrbitControls` while rail navigation is active.
- On wheel/touch, step the target index by `+1` or `-1`.
- Lerp camera position, look target, and zoom for a smooth transition.

## Rules

- Prefer real object positions over guessed heights.
- Keep the featured card near the center of the camera.
- Let neighboring cards remain visible for depth unless the reference demands isolation.
- Fix back-face text mirroring in the shader when cards are double-sided.
- Verify at least 3-4 scroll positions with `npm run visual:qa`.
