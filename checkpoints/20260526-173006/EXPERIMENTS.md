# Experiments

### 2026-05-25 - PatentVsem handmade static rewrite

- Goal: rewrite `https://patentvsem.ru/` as a separate handwritten site under `сайты Игорька/`, preserving the visible landing-page flow and lead forms.
- Checkpoint: `checkpoints/20260525-134728`.
- Changed: created `сайты Игорька/patentvsem-handmade/` with `index.html`, `styles.css`, `main.js`, `README.md`; retained original SEO metadata, anchor navigation, contacts, external links, Yandex.Metrika, map, main lead form, and floating callback popup.
- Checks: downloaded original Tilda HTML for inspection; `node --check` on `main.js`; `npm run qa`; Puppeteer desktop and mobile visual checks; callback popup open check.
- Result: desktop has no horizontal overflow, mobile `documentElement.scrollWidth` equals `clientWidth`, forms are present, popup opens, and browser console logs are clean. Preview screenshots saved as `preview-desktop.png` and `preview-mobile.png`.
- Lesson: Tilda form routing can be preserved temporarily by posting to `https://forms.tildacdn.com/procces/` with the discovered service ids, but production should move forms to a dedicated backend/CRM integration.

### 2026-05-25 - PatentVsem visual match pass

- Goal: make the handmade version visually match the original Tilda site instead of looking like a redesigned landing page.
- Checkpoint: `checkpoints/20260525-140841`.
- Changed: rebuilt the hero to the original yellow card geometry, restored the correct patent illustration asset, matched mobile hero coordinates, moved the intro/services/features/portfolio/stages blocks toward the original black/yellow visual system, and moved the service price/button below the service cards.
- Checks: Puppeteer desktop/mobile screenshots `final2-desktop-0.png`, `final2-desktop-1240.png`, `final2-desktop-2100.png`, `final2-desktop-3200.png`, `final2-mobile-0.png`; popup open check; `npm run qa`.
- Result: first desktop/mobile viewport now closely matches the original composition, with clean console logs, no horizontal overflow, two forms, and a working callback popup.

## Template

### YYYY-MM-DD - Название эксперимента

- Цель:
- Что изменили:
- Команда проверки:
- Результат:
- Вывод:

## Log

### 2026-05-20 - Агентская обвязка проекта

- Цель: дать агенту внешнюю память, правила проекта и проверяемый рабочий контур.
- Что изменили: добавлены markdown-файлы памяти, решений, экспериментов, задач и eval-критериев.
- Команда проверки: `npm run agent:status`, `npm run qa`.
- Результат: `npm run agent:status` проходит; первый `npm run qa` упал из-за проверки `carColor` при промпте про красную машину; после замены дефолтного промпта на `smoke-scene` `npm run qa` проходит.
- Вывод: markdown-слой установлен; дефолтный `qa` теперь нейтральный smoke-тест, а цветовые проверки лучше запускать отдельными сценариями.

### 2026-05-20 - Проверка инструментов

- Цель: понять, готово ли окружение к генерации и проверке сцен.
- Что изменили: ничего, только запущена проверка.
- Команда проверки: `npm run check:tools`.
- Результат: Node.js, npm, Puppeteer, Three.js и внешний 3D artist найдены; Blender не найден в PATH.
- Вывод: web/smoke-контур доступен, но для полного Blender-пайплайна нужно добавить Blender в PATH или указать путь в проектной конфигурации.

### 2026-05-20 - SQLite-память агента

- Цель: дать агенту локальную память на диске компьютера с поиском и тегами.
- Что изменили: добавлен `tools/agent_memory_db.py`, npm-команда `memory:db`, база `.agent_memory.sqlite3`.
- Команда проверки: `npm run memory:db -- import-md`, `npm run memory:db -- add "..." --tag system --tag memory`, `npm run memory:db -- stats`, `npm run memory:db -- search память`.
- Результат: база создана, 5 записей доступны, поиск работает.
- Вывод: теперь у агента есть локальная SQLite-память внутри workspace; она прозрачная и переносимая вместе с проектом.

### 2026-05-20 - Подключение Blender 5.1

- Цель: закрыть недостающий пункт `check:tools`, где Blender не находился.
- Что изменили: добавлены стандартные пути Blender 5.1 и 5.0 в `ToolRegistry._find_blender`.
- Команда проверки: `npm run check:tools`.
- Результат: `npm run check:tools` проходит; Blender найден по пути `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`.
- Вывод: проект находит установленный Blender без ручной переменной `BLENDER_PATH`.

### 2026-05-20 - Команды agent:context и agent:log

- Цель: дать агенту быстрый снимок проекта и простой способ записывать итоги задач.
- Что изменили: добавлены `tools/agent_context.py`, `tools/agent_log.py`, npm-скрипты `agent:context` и `agent:log`.
- Команда проверки: `npm run agent:status`, `npm run agent:context`, `npm run agent:log -- --title "..." --summary "..."`.
- Результат: `agent:status` и `agent:log` проходят; `agent:context` собирает workspace, scripts, tools, memory и tasks. Вложенный запуск Puppeteer QA из Python на этой Windows-среде таймаутится, поэтому QA оставлен отдельной прямой командой `npm run qa`.
- Вывод: контекст и логирование готовы; браузерный QA нужно запускать напрямую, не из Python-контекстника.

### 2026-05-20 - Оркестрация, checkpoints и memory pruning

- Цель: взять полезные идеи из мульти-агентной оркестрации, активной памяти, fail-safe и eval-цикла.
- Что изменили: добавлены `AGENT_ROLES.md`, `PERMISSIONS.md`, `evals/agent_operating_loop.md`, `tools/agent_checkpoint.py`, `tools/agent_evals.py`; SQLite-память получила поля `importance`, `access_count`, `last_accessed`, `archived`.
- Команда проверки: `npm run agent:checkpoint -- create "orchestration-memory-upgrade"`, `npm run agent:evals`, `npm run memory:db -- prune-candidates --limit 5`, `npm run qa`.
- Результат: checkpoint создан, agent evals проходят, memory pruning показывает кандидатов без удаления, QA проходит.
- Вывод: агент получил рабочую основу для режима оркестратора, наблюдаемости, checkpoint-восстановления и аккуратного забывания.

### 2026-05-20 - 3D-сцена по референсу с биомеханическим позвоночником

- Цель: создать сцену по приложенному референсу с темным cinematic-фоном, вертикальной металлической колонной и неоновыми частицами.
- Что изменили: добавлен `tools/create_reference_spine_scene.py`; финальные артефакты записаны в `output/scene.blend`, `output/scene.glb`, `output/preview.png`.
- Команда проверки: Blender background render, `npm run qa`, `npm run agent:evals`.
- Результат: внешний 3D artist сначала создал слишком generic primitive scene и вернул пути с mojibake; fail-safe fallback через кастомный Blender-скрипт успешно создал сцену и экспортировал артефакты.
- Вывод: для сложных визуальных референсов полезно использовать 3D artist как первый проход, но держать кастомный Blender fallback для точного art direction.

### 2026-05-20 - Исправление формы позвоночника

- Цель: сделать центральную колонну похожей именно на позвоночник из референса, а не на гладкие капсулы.
- Что изменили: в `tools/create_reference_spine_scene.py` позвонки перестроены как отдельные beveled bodies с фронтальными выпуклостями, темными выемками, округлыми губами, боковыми и крючковатыми отростками.
- Команда проверки: Blender background render, `npm run qa`, `npm run agent:evals`.
- Результат: `output/preview.png`, `output/scene.blend` и `output/scene.glb` обновлены; QA и agent evals проходят.
- Вывод: для узнаваемого позвоночника важнее силуэт каждого позвонка и промежутки между сегментами, чем просто вертикальный стек блестящих форм.

### 2026-05-20 - Честный показ текущей сцены

- Цель: не путать финальную сцену с промежуточными preview и неудачными attempts.
- Что изменили: добавлены `tools/scene_status.py`, `tools/scene_attempt.py`, npm-команды `scene:status` и `scene:attempt`.
- Команда проверки: `npm run scene:status`, `npm run scene:attempt -- snapshot "..."`, `npm run scene:attempt -- list`.
- Результат: `scene:status` показывает только финальные артефакты; `scene:attempt` сохранил текущую сцену в `output/attempts/20260520-134730-current-final-spine-scene`.
- Вывод: финальным источником правды является только `output/preview.png`; черновики хранятся отдельно в `output/attempts/`.

### 2026-05-20 - agent context and log tools

- Цель: agent context and log tools
- Что изменили: Added project context snapshot and task logging commands
- Команда проверки: `npm run agent:context`, `npm run agent:status`.
- Результат: Added project context snapshot and task logging commands
- Вывод: Запись создана через agent:log.

### 2026-05-20 - orchestration memory upgrade

- Цель: orchestration memory upgrade
- Что изменили: Added roles, permission control, checkpoints, evals, and active SQLite memory management
- Команда проверки: `npm run agent:evals`, `npm run qa`, `npm run memory:db -- prune-candidates --limit 5`.
- Результат: Added roles, permission control, checkpoints, evals, and active SQLite memory management
- Вывод: Запись создана через agent:log.

### 2026-05-20 - reference 3d spine scene

- Цель: reference 3d spine scene
- Что изменили: Created custom Blender scene from reference after external artist fallback
- Команда проверки: `Blender background render`, `npm run qa`, `npm run agent:evals`.
- Результат: Created custom Blender scene from reference after external artist fallback
- Вывод: Запись создана через agent:log.

### 2026-05-20 - spine anatomy revision

- Цель: spine anatomy revision
- Что изменили: Rebuilt the central column with anatomy-like vertebra bodies, lips, recesses, side processes, and hooks
- Команда проверки: `Blender background render`, `npm run qa`, `npm run agent:evals`.
- Результат: Rebuilt the central column with anatomy-like vertebra bodies, lips, recesses, side processes, and hooks
- Вывод: Запись создана через agent:log.

### 2026-05-20 - honest scene preview pipeline

- Цель: honest scene preview pipeline
- Что изменили: Added scene:status and scene:attempt so only output/preview.png is treated as current scene and drafts are archived separately
- Команда проверки: `npm run scene:status`, `npm run scene:attempt -- list`, `npm run agent:evals`, `npm run qa`.
- Результат: Added scene:status and scene:attempt so only output/preview.png is treated as current scene and drafts are archived separately
- Вывод: Запись создана через agent:log.

### 2026-05-21 - visual QA and meta autolog upgrade

- Цель: visual QA and meta autolog upgrade
- Что изменили: Created tools/visual_qa.js, added visual:qa script, extended agent_log meta fields, updated eval coverage
- Команда проверки: `npm run visual:qa -- --url http://127.0.0.1:5178/ --steps 4`, `npm run agent:evals`.
- Результат: npm run visual:qa -- --url http://127.0.0.1:5178/ --steps 4; npm run agent:evals
- Вывод: Use visual:qa after 3D/frontend work and agent:log --meta-strategy to record task outcomes into meta-learning.

### 2026-05-21 - max agent upgrade

- Цель: max agent upgrade
- Что изменили: Created agent:goal, visual:match, patterns library, max upgrade eval, and improved meta strategy fallback by domain
- Команда проверки: `npm run agent:evals`, `npm run visual:match -- --reference visual-qa/frame-00.png --candidate visual-qa/frame-00.png`.
- Результат: npm run agent:evals; visual:match smoke PASS with identical images; visual:match REVIEW against real reference as expected
- Вывод: For maximum local autonomy, use agent:goal for task queues, patterns/ for reusable solutions, visual:qa for browser output, visual:match for reference heuristics, and agent:meta for strategy choice.
### 2026-05-21 - reference visual tuning for external site

- Goal: tune `C:\Users\Ардор\OneDrive\Рабочий стол\сайт с 3д` toward the provided Active Theory-like references: darker teal/green grade, closer card scale, denser colored dust, more iridescent spine and glassy card surfaces.
- Changed: updated external site `styles.css` and `main.js`; added `tools/site_render_check.js` for future heavyweight external-site render checks.
- Checks: `node --check main.js`; `node --check tools/site_render_check.js`; `npm run qa`; `npm run check:tools`; `npm run agent:evals`.
- Result: syntax and standard QA passed. `npm run visual:qa -- --url http://127.0.0.1:5180/ --steps 3` and `tools/site_render_check.js` timed out in Puppeteer while opening the heavy external GLB site, so final browser screenshot still needs a manual or fixed-Puppeteer pass.
- Lesson: for large external GLB sites, avoid assuming the default Puppeteer navigation timeout is enough; keep a dedicated no-cache render checker and consider reducing scene weight only if the real browser also struggles.

### 2026-05-21 - deployed reference iteration loop

- Goal: use `https://youjin-led.github.io/3d-form/` as source of truth and iterate without waiting for manual user QA.
- Changed: pushed the site to `Youjin-led/3d-form`, deployed through `gh-pages`, replaced mirrored card texture text with readable sprite labels, faded inactive labels on scroll, softened card noise, removed favicon 404, and replaced built-in uniform GLB stars with controlled dust clouds.
- Checks: repeated Puppeteer screenshots on deployed URL: `deployed-pass8.png`, `deployed-pass9.png`, `deployed-pass10.png`, `deployed-fade-scroll-0.png`, `deployed-fade-scroll-1.png`, `deployed-fade-scroll-2.png`; `node --check main.js`; GitHub push to `main` and `gh-pages`.
- Result: deployment loads with `window.__SCENE_READY === true`, no console errors after favicon fix, active card labels are readable and scroll states no longer show strong floating labels from inactive cards.
- Lesson: for this GLB, card UVs are unreliable for text; draw readable labels as camera-facing sprites and dynamically fade by `cardRail.targetIndex`.

### 2026-05-22 - autonomous deployed polish continuation

- Goal: continue improving deployed `https://youjin-led.github.io/3d-form/` without waiting for manual QA after each pass.
- Changed: added dense bitmap particle cluster planes, reduced card grain, balanced foreground clusters away from the side menu, added a reference-style top-right rail control, and added a dark readability field behind the left menu.
- Checks: `node --check main.js`; GitHub push to `main` and `gh-pages`; HTTP checks confirmed deployed `index.html` includes `rail-control` and deployed `main.js` includes `updateRailControl`, `makeParticleClusterTexture`, and `cardTextSprites`; `npm run agent:evals`.
- Result: last successful Edge screenshot `deployed-edge-check.png` showed denser colored particle clusters and readable active card labels. Later Chromium/Edge launches intermittently timed out before opening the page, so browser QA needs a fresh headless process cleanup before the next visual screenshot series.
- Lesson: continue using Edge with clean profiles for visual QA when bundled Chromium stalls; avoid stopping work solely because one screenshot attempt fails, but record tool instability separately from site quality.

### 2026-05-22 - deployed dust and spine correction

- Goal: fix user complaint that dust clusters looked like flat 2D planes while rotating, and push the spine silhouette closer to the supplied references.
- Changed: removed flat nebula/cardboard dust planes from `main.js`; moved particle creation after GLB load; reduced billboard point density; added small instanced 3D shard clouds; expanded procedural spine augmentation to 13 vertebrae with dorsal spikes, lateral processes, hooks, and rib-like protrusions.
- Checks: `node --check main.js`; `npm run qa`; pushed commits `0d1b8f4`, `4844963`, and `0990d02` to `main` and `gh-pages`; verified deployed `main.js` contains `volumetricShardCloud`, `const count = 13`, `dorsalGeo`, and `ribGeo`; captured live GitHub Pages screenshots from Chrome headless.
- Result: deployed page loads from `https://youjin-led.github.io/3d-form/`; flat 2D dust planes are removed; black shard artifacts from the first instanced pass were corrected by switching shards to smaller additive `MeshBasicMaterial` geometry.
- Lesson: for this scene, use GitHub Pages as the visual source of truth after each push. Avoid large flat particle textures; use either sparse point fields or instanced 3D shards for dust near the spine.

### 2026-05-22 - Blender-source dust and spine pass

- Goal: move visual work back into Blender/GLB instead of building a second procedural spine in site JS; keep current scene restorable.
- Changed: created checkpoint `checkpoints/20260522-110016` and scene attempt `output/attempts/20260522-110247-before-blender-reference-dust-spine-pass`; added `tools/refine_scene_reference_pass.py`; refined existing `real_nih_lumbar_vertebra_*` transforms/materials; added smaller real 3D mesh dust in `output/scene.blend`; exported `output/scene.glb`; copied it to the site; changed viewer to stop generating JS dust and to show GLB dust while hiding constellation/ribbon helpers.
- Checks: Blender save/export/render completed; `npm run scene:status`; `node --check main.js`; `npm run qa`; local Chrome screenshot `local-blender-scene-viewer-v3.png`.
- Result: local viewer shows the anatomical spine retained, visible volumetric dust, and no separate procedural spine column. Further passes should continue in Blender first, then use the site only as preview/deploy.
- Lesson: main.js should behave as a viewer. Do not add fake spine geometry in JS; keep spine changes in `output/scene.blend` and always snapshot before changing anatomy.

### 2026-05-22 - reverted wrong Blender spine overlay pass

- Goal: correct the mistaken approach where extra primitive anatomy was layered over the spine instead of editing the duplicated vertebra source.
- Reverted: restored `output/scene.blend`, `output/scene.glb`, `output/preview.png`, and `output/report.json` from `output/attempts/20260522-132849-before-anatomy-one-to-one-reference-spine-pass`; deleted `tools/refine_spine_anatomy_match_pass.py`.
- Result: the scene is back to the pre-overlay state. Next pass must edit the repeated vertebra unit itself and then duplicate/rotate it with visible gaps, matching the reference structure.
- Lesson: do not add plate-like helper geometry on top of the spine. The user wants one improved vertebra part, duplicated with small rotations and spacing.

### 2026-05-22 - corrected repeated vertebra unit pass

- Goal: refine the spine using the user's intended structure: one downloaded vertebra part, slightly modified, then repeated with gaps and small rotations.
- Snapshot: `output/attempts/20260522-143033-before-corrected-repeated-vertebra-unit-pass`.
- Changed: added `tools/refine_repeated_vertebra_unit_pass.py`; edited the local mesh shape of each repeated NIH vertebra copy, assigned the wet iridescent material, added subtle worn/pitted modifiers to the repeated unit, increased vertical spacing, reduced per-copy height, and added small per-copy rotations.
- Checks: Blender background save/export/render; `npm run scene:status`; `npm run qa`; `npm run agent:evals`; `tools/diagnose_spine_parts.py`.
- Result: final `output/scene.blend`, `output/scene.glb`, and `output/preview.png` are updated. Diagnostics show copy centers spaced by about `0.92` with copy heights mostly around `0.86-1.08`, so the column now has visible gaps instead of a continuous overlapped tube.
- Lesson: when matching this reference, first validate the repeated-unit spacing numerically before judging the render, because card occlusion can hide whether the spine construction itself is correct.

### 2026-05-22 - card-hidden side-angle vertebra refinement

- Goal: use the extra side-angle references and temporarily hide cards so the Blender spine can be judged without foreground occlusion.
- Snapshot: `output/attempts/20260522-150626-before-further-repeated-vertebra-self-check-refinement`.
- Changed: updated `tools/refine_repeated_vertebra_unit_pass.py` to hide all `spiral_project_card_*` objects for the sculpt-check render, rotate the repeated vertebra copies into a side-profile orientation, tighten copy spacing, add additional local mesh shaping passes (`v4-v6`), and strengthen the wet purple-blue material.
- Checks: repeated Blender background save/export/render cycles; `tools/diagnose_spine_parts.py`; `npm run qa`; `npm run scene:status`; `npm run agent:evals`.
- Result: final `output/preview.png` now shows the spine without cards, built from repeated copies with visible gaps and a more side-oriented vertebra profile. It is closer than the previous front-facing ring/stack view, though further sculpting can still improve the individual vertebra silhouette if stricter one-to-one matching is required.
- Lesson: when the imported vertebra reads like rings, rotating the repeated part itself matters more than orbiting the camera. Hide cards during anatomy passes, then re-enable/composite them only after the spine silhouette is correct.

### 2026-05-22 - reversed tilt with subtle right spiral

- Goal: correct the user's direction note: keep the general tilt feel, reverse its direction, and add only a barely visible rightward spiral through the repeated vertebra column.
- Snapshot: `output/attempts/20260522-155422-before-reversing-vertebra-tilt-and-adding-subtle-right-spiral`.
- Changed: updated `tools/refine_repeated_vertebra_unit_pass.py` orientation math by mirroring the main vertebra tilt, reducing per-copy twist, and adding a tiny center offset phase so the column has a very soft rightward spiral instead of a strong screw shape.
- Checks: Blender background save/export/render; `npm run qa`; `npm run scene:status`.
- Result: final `output/preview.png`, `output/scene.blend`, and `output/scene.glb` are updated with the corrected tilt direction and subtle right-turning stack.
- Lesson: for user-directed anatomical posing, treat "spiral" as very small cumulative per-copy rotation plus slight center drift, not a large visible twist.

### 2026-05-22 - stronger visible reverse tilt

- Goal: make the reversed tilt and rightward spiral actually visible after the user noted the first correction was too subtle.
- Snapshot: `output/attempts/20260522-161807-before-stronger-visible-reverse-tilt-and-right-turn`.
- Changed: increased the mirrored visible roll/side tilt, widened the tiny center drift, and strengthened the cumulative rightward rotation while keeping it below a hard screw-like twist.
- Checks: Blender background save/export/render; `npm run qa`; `npm run scene:status`.
- Result: final `output/preview.png`, `output/scene.blend`, and `output/scene.glb` now show a visibly reversed column tilt with a readable but still soft rightward spiral.
- Lesson: if the user says a pose correction is invisible, prioritize visible silhouette change in the render over small numeric rotation changes.

### 2026-05-22 - relative per-copy spiral correction

- Goal: fix the user's note that the whole column looked rotated as one piece; the spiral must come from each vertebra turning relative to its neighbors.
- Snapshot: `output/attempts/20260522-164810-before-relative-copy-counter-rotation-correction`.
- Changed: replaced simple Euler angle tweaks with ordered rotation matrices so yaw is applied as a real per-copy rightward turn before the reverse tilt; reduced center drift, then increased the neighbor-to-neighbor yaw enough to be visible in the final preview.
- Checks: repeated Blender background save/export/render and manual inspection of `output/preview.png`.
- Result: final `output/preview.png`, `output/scene.blend`, and `output/scene.glb` now show a progressive segment-to-segment turn instead of a uniformly rotated stack.
- Lesson: in this scene, "spiral" means accumulated relative yaw between duplicated vertebra units; camera orbit or whole-column rotation is the wrong visual cue.

### 2026-05-22 - baked Blender scene transferred to site

- Goal: move the final Blender spine scene to the actual local site with the same colors/material feel, without rebuilding it procedurally.
- Checkpoint: `checkpoints/20260522-171322`.
- Changed: copied final `output/scene.glb` and `output/preview.png` into `C:\Users\Ардор\OneDrive\Рабочий стол\сайт с 3д\assets`; added `BAKED_SPINE_VIEW` to the external site's `main.js` so cards are hidden, card rail is disabled, and the camera frames the vertebra bbox while retaining the browser spine/dust material shaders.
- Checks: `node --check` on the external `main.js`; external site served on `http://127.0.0.1:5181/`; Puppeteer screenshot `site-baked-spine.png`; browser reported `ready: true`, `cards: 0`, no console errors; `npm run qa`; `npm run scene:status`.
- Result: the website now loads the updated final GLB instead of the old asset and opens directly on the baked spine view.
- Lesson: when port `5177` is already occupied by the repo preview server, verify `main.js` contents over HTTP before trusting browser QA; use a fresh port for the external site.

### 2026-05-22 - restored scene cards on baked site

- Goal: restore the 3D scene's own cards on the site after the user asked for the same cards back.
- Checkpoint: `checkpoints/20260522-180107`.
- Changed: kept the final GLB as the source, made `spiral_project_card_*` / `reference_card_*` meshes visible again, restored card rail targeting from GLB card positions, and skipped extra readable text sprites in baked mode so the visible cards come from the scene geometry.
- Checks: `node --check` on the external `main.js`; Puppeteer screenshot `site-scene-cards-restored.png`; browser reported `ready: true`, `visibleCards: 30`, `rail: 15`, no console errors; `npm run qa`; `npm run scene:status`.
- Result: the local site on `http://127.0.0.1:5181/` now opens with the spine plus restored 3D scene cards.
- Lesson: if the user asks for "cards from the 3D scene", keep GLB card meshes and rail positions; avoid adding separate text sprite overlays in baked mode.

### 2026-05-23 - imported Blender camera and card transforms for site

- Goal: fix the wrong site card arrangement and remove the white overexposure after restoring cards.
- Checkpoint: `checkpoints/20260523-005331`; attempt: `output/attempts/20260523-005331-before-restoring-cards-for-site-export`.
- Changed: added `tools/restore_cards_for_site_pass.py` to re-enable the existing `spiral_project_card_*` objects before final GLB export; copied the refreshed `output/scene.glb` and `output/preview.png` to the external site; changed the site to use the imported orthographic Blender camera from the GLB instead of a hand-built bbox camera; replaced the overbright card shader with a muted non-emissive card material; reduced site exposure and bloom.
- Checks: Blender save/export/render completed; `node --check` on the external `main.js`; Puppeteer screenshots `site-scene-cards-imported-camera.png` and `site-scene-cards-imported-camera-low-bloom.png`; browser reported `ready: true`; `npm run qa`; `npm run scene:status`.
- Result: cards now come from Blender scene-space transforms and the site camera comes from the GLB camera. The first source/shader attempts caused severe white bloom, so the final viewer keeps bloom low and cards non-emissive.
- Lesson: do not manually convert Blender camera coordinates for GLB scenes. Import the GLTF camera and copy its world transform/projection scale; otherwise the site composition will not match Blender.

### 2026-05-23 - matched published card rail and scroll

- Goal: match the camera/card layout and wheel-driven camera movement from `https://youjin-led.github.io/3d-form/`.
- Checkpoint: `checkpoints/20260523-120201`.
- Changed: inspected the published `main.js`; captured the live reference site's `__CARD_RAIL` and `spiral_project_card_*` transforms into `reference-card-layout.json`; embedded the 30 published card transforms into the external site's `main.js`; switched baked camera mode off so `buildCardRail`, wheel, touch, and nav buttons behave like the published site; adjusted exposure/bloom for the current brighter GLB while keeping the reference rail camera stops.
- Checks: `node --check` on the external `main.js`; Puppeteer online screenshots `reference-online-start.png` / `reference-online-after-wheel.png`; local screenshots `site-reference-layout-balanced-start.png` / `site-reference-layout-balanced-after-wheel.png`; local browser reported `rail: 15`, first rail camera `[-3.611, 6.780, 9.128]`, label changed from `01 - SUSTAINABLE` to `02 - E.C.H.O.` after wheel; `npm run qa`; `npm run scene:status`.
- Result: local site card placement, first camera stop, and wheel-driven rail movement now match the published site behavior. Visual exposure is slightly reduced because the current GLB contains brighter restored scene particles than the published asset.
- Lesson: for matching a deployed interactive scene, capture runtime transforms/rail stops from the browser and replay them locally; source code parity alone is not enough when the GLB assets have diverged.

### 2026-05-24 - S-curve spine posture

- Goal: reshape the repeated vertebra chain so the parts follow the anatomical S-curve from the new reference, while preserving the site cards and published scroll layout.
- Checkpoint: `checkpoints/20260524-210048`; attempt: `output/attempts/20260524-210050-before-s-curve-spine-posture`.
- Changed: updated `tools/refine_repeated_vertebra_unit_pass.py` so the visible duplicated vertebrae use a sagittal S-curve X offset, tangent-based pitch, subtle per-copy yaw, and slightly slimmer per-copy scale; restored scene cards afterward and copied the refreshed `output/scene.glb` / `output/preview.png` to the external site.
- Checks: Blender save/export/render completed; inspected final `output/preview.png`; captured `site-scurve-spine.png` with headless Chrome; `npm run qa`; `npm run scene:status`.
- Result: the final scene artifacts now show the vertebra parts bending along an S-shaped anatomical posture instead of a straight column, with the site still loading the cards and rail UI.
- Lesson: this posture reads best when driven by object locations along a sagittal curve plus local tangent rotation; rotating the whole spine or only changing yaw does not create the anatomical silhouette the user is asking for.

### 2026-05-24 - anchored jellyfish card drift

- Goal: make every project card keep moving like a small jellyfish path while staying close to its published layout anchor.
- Checkpoint: `checkpoints/20260524-215308`.
- Changed: added `floatingCards` state in the external site's `main.js`, stored each `spiral_project_card_*` object's base position/quaternion after published layout normalization, and applied small per-card figure-eight offsets plus subtle rotation wobble each frame; readable text sprites inherit the same local offset.
- Checks: `node --check` on the external `main.js`; local site served on `http://127.0.0.1:5181`; compared `site-card-float-early.png` and `site-card-float-late.png`; `npm run qa`.
- Result: cards now continuously drift in a small radius around their original positions instead of staying static or moving through the whole scene.
- Lesson: keep rail stops static and animate only the card meshes around stored base transforms; otherwise scroll targeting would chase moving geometry and feel unstable.

### 2026-05-24 - full-space card routes

- Goal: make cards travel through the scene on defined routes while keeping the soft jellyfish-like wobble and slightly faster motion.
- Checkpoint: `checkpoints/20260524-225430`.
- Changed: expanded `getCardFloatOffset` from a small local drift into large deterministic elliptical/vertical paths, increased route and wobble speeds, and damped the original anchor contribution so edge cards do not fly too far outside the camera frame.
- Checks: `node --check` on the external `main.js`; local site served on `http://127.0.0.1:5181`; compared `site-card-routes-early.png` and `site-card-routes-late.png`; `npm run qa`.
- Result: cards now move through a broad part of the scene instead of staying around fixed anchor points, while retaining gentle rotation/pulse motion.
- Lesson: when moving cards through the whole composition, large offsets should be partially recentred against their original layout positions; otherwise high/side anchor cards quickly leave the useful viewport.

### 2026-05-25 - card and spine collision response

- Goal: stop moving cards from passing through each other or through the spine; contacts should make them bounce away.
- Checkpoint: `checkpoints/20260524-225430`.
- Changed: added `cardBodies` as per-card collision bodies for paired `image`/`edge` meshes, stored collision offsets/velocities, added card-card repulsion, 3D spine cylinder repulsion, screen-space card-card repulsion, and a wider screen-space spine corridor so visible overlap is pushed apart even when depth differs.
- Checks: `node --check` on the external `main.js`; local site served on `http://127.0.0.1:5181`; captured `site-card-collisions-late.png`; `npm run qa`.
- Result: cards now keep their full-scene routes but gain collision impulses that push them away from neighboring cards and from the spine area instead of visually passing through.
- Lesson: for this transparent 3D scene, collision must include screen-space separation, not only world-space distance, because visually overlapping transparent planes can look like intersection even when their Z positions differ.

### 2026-05-26 - card hover focus

- Goal: make a hovered project card advance toward the screen in a visible, polished way while keeping the moving-card/collision scene intact.
- Checkpoint: `checkpoints/20260526-014106`.
- Changed: added pointer raycasting against the `spiral_project_card_*` meshes, per-card hover state, eased scale/forward camera offset, lifted render order during focus, and matching movement for readable text sprites. Hover is latched while the card slides forward so it does not cancel itself by moving away from the ray.
- Checks: `node --check` on the external `main.js`; local site served on `http://127.0.0.1:5181`; Puppeteer found a hovered card and captured `site-card-hover-focus.png`; no browser console errors; `npm run qa`.
- Result: cards still follow their animated routes and collision response, but the hovered card now smoothly pushes forward and enlarges instead of staying flat in the scene.
- Lesson: raycast hover for animated 3D cards needs a small hover latch/dead-zone; otherwise the card moves out from under the cursor and immediately clears its own hover state.

### 2026-05-26 - static hover focus lock

- Goal: stop the focused card from continuing its jellyfish route after it has advanced toward the screen.
- Changed: capture the hovered card and text sprite position/quaternion at hover start, blend from the live route into that frozen pose plus the camera-forward focus offset, then snap hover amount to `1` once it is visually settled.
- Checks: `node --check` on the external `main.js`; Puppeteer hover-static probe captured `site-card-hover-static.png`; sampled card position after settling had `delta: 0` over 1.4 seconds; no browser console errors; `npm run qa`.
- Result: the hovered card now becomes static once it has moved forward, while non-hovered cards continue moving normally.
- Lesson: for a focused 3D card, freezing the source pose is more reliable than only easing the current animated route; otherwise route motion keeps leaking into the focus state.

### 2026-05-26 - centered face-camera hover

- Goal: make the hovered card rotate flat toward the viewer, land in the screen center, and prevent other moving cards from passing visually in front of it.
- Changed: replaced the old world-offset hover with a camera-space focus target at viewport center, slerped the focused card to the camera quaternion, raised focused card/text render order, and disabled depth testing on the focused card while it is active.
- Checks: `node --check` on the external `main.js`; Puppeteer focus probe captured `site-card-hover-centered.png` and reported center distance `0`, quaternion dot `1`, renderOrder `122`, depthTest `false`; no browser console errors; `npm run qa`.
- Result: a hovered angled card now turns square-on, moves to the exact screen center, and stays above the rest of the moving cards.
- Lesson: a hover overlay in an orthographic Three.js scene should be solved in camera space, not by tweaking world-space X/Y offsets.

### 2026-05-26 - slower card motion

- Goal: make the ambient card movement a little calmer without changing hover focus behavior.
- Changed: added `CARD_MOTION_SPEED = 0.78` and routed the card position/rotation oscillators through that multiplier.
- Checks: `node --check` on the external `main.js`; `npm run qa`.
- Result: card routes and rotation wobble now move about 22% slower while preserving the same path shapes.

### 2026-05-26 - half-size cards

- Goal: make the project cards half as wide.
- Changed: reduced `PUBLISHED_CARD_TARGET_WIDTH` from `3.85` to `1.925`, so the imported card meshes are scaled to half their previous published width while keeping their proportions.
- Checks: `node --check` on the external `main.js`; `npm run qa`.
- Result: cards render at half the previous target width and retain the existing motion/hover logic.

### 2026-05-26 - responsive scene layout

- Goal: make the published 3D scene look composed on desktop, tablets, portrait phones, and landscape phones.
- Checkpoint: `checkpoints/20260526-133147`.
- Changed: added viewport-aware orthographic camera height, card scale/distance, rail zoom, hover focus distance, text scale, and mobile/tablet CSS for the top nav, rail control, side menu, loading state, and safe-area spacing.
- Checks: `node --check` on the external `main.js`; responsive Puppeteer probe for `1440x900`, `834x1112`, `390x844`, and `844x390`; screenshots `responsive-desktop.png`, `responsive-tablet.png`, `responsive-mobile.png`, `responsive-mobile-landscape.png`; `npm run qa`.
- Result: UI controls stay inside the viewport on all tested sizes, the scene stays visible, and mobile layouts use smaller cards plus wider camera framing instead of cropping the spine/card composition.
- Lesson: the 3D canvas needed responsive camera math as much as CSS; only moving DOM controls would leave the orthographic scene too tightly cropped on portrait screens.

### 2026-05-25 - PatentVsem lower-page visual alignment

- Goal: continue the handmade PatentVsem rewrite from the previous pass and align the lower desktop/mobile screenshots with the original Tilda site.
- Checkpoint: `checkpoints/20260525-142806`.
- Changed: made the header fixed like the original during scroll, widened and shifted the contacts/map layout, restored the consultation form subtitle, adjusted the contacts vertical offset, and kept all edits isolated under `сайты Игорька/patentvsem-handmade`.
- Checks: targeted desktop screenshots `quick9-local-desktop-6400.png`, `quick9-local-desktop-7200.png`, `quick9-local-desktop-8000.png`; targeted mobile screenshots `quick9-local-mobile-0.png`, `quick9-local-mobile-7000.png`, `quick9-local-mobile-9800.png`; `node --check` on `main.js`; `npm run qa`.
- Result: lower-page rhythm now lines up with the original reference much more closely: sticky header remains visible, contacts begin at the same scroll band, and the consultation form appears at the same lower-page position.
- Lesson: disable smooth scrolling in screenshot automation before comparing fixed scroll offsets; otherwise Puppeteer can capture mid-animation frames and make sections look incorrectly shifted.

### 2026-05-26 - 3d-form-2 work copy jellyfish replacement

- Goal: create a second working version where the project cards are replaced by beautiful jellyfish-like 3D objects while preserving the spine scene, card routes, collision, rail, and hover behavior.
- Work folder: `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2`; preserved baseline remains `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_saved_responsive_2026-05-26`.
- External model check: Sketchfab downloadable model API required authentication; Meshy jellyfish catalog appeared to require account/download flow, so no third-party model was embedded.
- Changed: added procedural Three.js jellyfish groups in `main.js` with translucent colored bells, glowing rims, animated tentacles, aura sprites, invisible hover proxies, and reused existing card movement/collision/hover machinery.
- Checks: `node --check main.js`; local browser check on `http://127.0.0.1:5182` reported `ready: true`, `jellyfish: 15`, `floating: 15`, `rail: 15`, no page errors; hover check targeted `jellyfish_01` and reported `hovered: 1`; screenshot `jellyfish-v2-desktop-final.png`; root `npm run qa` passed.
- Lesson: for this scene, procedural jellyfish are more controllable than account-gated external GLB downloads, and replacing the visual mesh while keeping card anchors preserves the polished route/hover system.
