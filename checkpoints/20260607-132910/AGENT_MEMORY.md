# Agent Memory

- 2026-06-03: Candle site MVP: active frontend surface is now a static Lumiere Atelier candle storefront in `index.html`, `styles.css`, and `main.js`. It uses local canvas-generated candle/product visuals, catalog filters, set presets, cart drawer, and a lead form. Next useful upgrades: real product photos/brand assets and a real lead endpoint. Checks passed: `npm run check:tools`, `node --check main.js`, `npm run qa`, desktop/mobile Puppeteer visual smoke. --tags candles,frontend,mvp,qa

- 2026-06-03: Candle site direction refined: user wants the essence of `https://meliponini.ru/svechi`, but more aesthetic and simple, with a calculator and integrations to messengers/email. Current implementation uses a red/blue/wine/blush palette-first visual, compact preorder calculator, and generated Telegram/WhatsApp/email/clipboard order text. Replace placeholder contact values with real business contacts later. --tags candles,requirements,frontend,integrations

- 2026-06-03: Candle cards requirement: do not prefill public product cards yet. Cards should be user-managed through an admin surface. Current prototype has an in-page local admin storing cards in `localStorage` under `lumiere-candle-products`; public catalog is empty until admin-created cards exist. --tags candles,admin,requirements,localstorage

- 2026-06-03: Candle visual reference clarification: the red/blue/wine/blush screenshot should not be inserted as an image or asset. Use it only as the site's color palette and typographic mood. Current page has zero `<img>` tags and uses CSS/canvas-generated palette accents only. --tags candles,visual-reference,palette,requirements

- 2026-06-03: Candle structure clarification: user wants `https://meliponini.ru/` homepage structure as the base, not the color screenshot as a layout block. Current site structure: promo strip, nav, hero, category directions, social/social CTA, catalog filled by admin, calculator, wholesale, about, admin, contacts, footer. Palette remains red/blue/wine/blush. --tags candles,structure,meliponini,requirements

- 2026-06-03: Candle header navigation should stay simple with only three top links: `Калькулятор`, `Каталог`, `Контакты`. Keep other sections accessible from page content/footer if needed, but do not crowd the top bar. --tags candles,header,nav,requirements

- 2026-06-03: Candle site simplified further: the page body should expose only three main sections after the hero: `catalog`, `calculator`, and `contacts`. The catalog section may contain the local admin panel for adding cards, but there should be no separate wholesale/about/social/category-carousel sections unless the user asks to add them back. --tags candles,sections,requirements,simplified

- 2026-06-04: Candle site navigation update supersedes the earlier three-section simplification. The visible catalog tab should be removed. Current top/footer tabs are `Калькулятор`, `Отзывы`, `Партнеры`, `Товары для свечеваров`, `Оптовые продажи`, `Контакты`. The local card admin now lives under `maker-goods` / `Товары для свечеваров`. --tags candles,nav,sections,requirements,current

- 2026-06-05: Current candle site section order now matches nav: `calculator`, `reviews`, `partners`, `maker-goods`, `wholesale`, `contacts`. Maker-goods has 8 categories: `Красители`, `Вощина`, `Цветные воски`, `Отдушки`, `Тара`, `Упаковка`, `Силиконовые формы`, `Фитили`. Wholesale has 12 categories including candles, bath/body care, gift sets, diffusers/autoparfume, and room sprays. Hero copy now says `Свечи, ароматы и наборы для дома и ухода`. --tags candles,current,sections,categories,hero

- 2026-06-05: Latest ecommerce structure supersedes previous section order. Current page flow: hero, `directions`, `calculator`, `wholesale`, `maker-goods`, `partners`, `reviews`, `contacts`. Header nav order: `Калькулятор`, `Оптовые продажи` dropdown, `Товары для свечеваров` dropdown, `Партнеры`, `Отзывы`, `Контакты`, plus `Оставить заявку` CTA. --tags candles,current,ecommerce-structure,nav

- 2026-06-05: Candle site is now multipage rather than one long scroll. Current pages: `index.html` home, `calculator.html`, `wholesale.html`, `maker-goods.html`, `partners.html`, `reviews.html`, `contacts.html`. Shared `main.js` is page-safe and supports `calculator.html?direction=...` preselection. --tags candles,current,multipage,structure

Этот файл хранит долговременные заметки для работы агента в проекте.

## Stable Preferences

- Пользователь предпочитает русский язык общения.
- Для автономной работы агенту нужна внешняя память, явные проектные правила и проверяемый QA-контур.

## Notes

- 2026-05-20: Создана markdown-обвязка памяти: `AGENTS.md`, `PROJECT_RULES.md`, `DECISIONS.md`, `EXPERIMENTS.md`, `TASKS.md`, `evals/`.
- 2026-05-20: Добавлена локальная SQLite-память `.agent_memory.sqlite3` через `tools/agent_memory_db.py` и команду `npm run memory:db`.
- 2026-05-20: Blender установлен по пути `C:\Program Files\Blender Foundation\Blender 5.1\blender.exe`; `ToolRegistry` умеет находить Blender 5.1 и 5.0.
- 2026-05-20: Добавлены команды `agent:context` для снимка проекта и `agent:log` для записи итогов задач в SQLite и markdown-журналы.
- 2026-05-20: Добавлены роли оркестрации, permission control, checkpoints, agent evals и активное управление SQLite-памятью через importance/access_count/archive.
- 2026-05-20: Для честного показа сцены добавлены `scene:status` и `scene:attempt`; текущей сценой считается только `output/preview.png`, а промежуточные рендеры хранятся в `output/attempts/`.

- 2026-05-20: agent context and log tools: Added project context snapshot and task logging commands Checks: npm run agent:context; npm run agent:status.

- 2026-05-20: orchestration memory upgrade: Added roles, permission control, checkpoints, evals, and active SQLite memory management Checks: npm run agent:evals; npm run qa; npm run memory:db -- prune-candidates --limit 5.

- 2026-05-20: reference 3d spine scene: Created custom Blender scene from reference after external artist fallback Checks: Blender background render; npm run qa; npm run agent:evals.

- 2026-05-20: spine anatomy revision: Rebuilt the central column with anatomy-like vertebra bodies, lips, recesses, side processes, and hooks Checks: Blender background render; npm run qa; npm run agent:evals.

- 2026-05-20: honest scene preview pipeline: Added scene:status and scene:attempt so only output/preview.png is treated as current scene and drafts are archived separately Checks: npm run scene:status; npm run scene:attempt -- list; npm run agent:evals; npm run qa.

- 2026-05-20: 3D scene workflow preference: for future projects, prioritize form/silhouette first, then tune color and lighting to the reference. User explicitly said: 'фокус формами ... цвет подтяни под референс'. --tags 3,workflow,preference

- 2026-05-21: For future 3D/frontend work, run an internal role checklist before final delivery: Art Director, Camera/Interaction Designer, Shader/Materials Specialist, Reference Matcher, Performance QA, Memory Curator, Safety Reviewer. Preferred order: match form/composition first, then color/materials, then camera/interaction, then verify the real final canvas/site output. --tags 3d,frontend,workflow,roles,preference

- 2026-05-21: Meta-learning preference: start with a safe local prototype that records task episodes and chooses strategies from SQLite data before attempting LLM-generated recursive self-improvement. Strategy candidates may be created by analysis, but code/prompt rewrites require explicit user intent. --tags meta-learning,strategy,safety,preference

- 2026-05-21: visual QA and meta autolog upgrade: Added visual:qa browser screenshots and meta episode autologging through agent:log Checks: npm run visual:qa -- --url http://127.0.0.1:5178/ --steps 4; npm run agent:evals. Lesson: Use visual:qa after 3D/frontend work and agent:log --meta-strategy to record task outcomes into meta-learning.

- 2026-05-21: max agent upgrade: Added goal runner, reference matcher, pattern library, and stronger eval coverage Checks: npm run agent:evals; npm run visual:match -- --reference visual-qa/frame-00.png --candidate visual-qa/frame-00.png. Lesson: For maximum local autonomy, use agent:goal for task queues, patterns/ for reusable solutions, visual:qa for browser output, visual:match for reference heuristics, and agent:meta for strategy choice.

- 2026-05-23: Assistant chosen name for this project/user relationship: "Iskra" / "Искра". User asked the assistant to choose and remember its own name.

- 2026-05-23: Hugging Face Inference readiness: installed Python user packages `openai` 2.38.0, `huggingface_hub` 1.16.1, and `pillow` 12.2.0. Real HF calls still require `HF_TOKEN` in the environment and explicit permission for network use.

- 2026-05-23: Added `tools/hf_inference.py` and npm script `hf:infer` for Hugging Face checks, chat calls through `https://router.huggingface.co/v1`, and image generation. Use `npm.cmd run hf:infer -- check` on Windows PowerShell.

- 2026-05-25: Tilda rewrite/new client sites must live only under `сайты Игорька/`; do not mix those files with the existing 3D project or root artifacts.

- 2026-05-25: Do not call the user Igor. 'Igor' belongs to the PatentVsem site/contact context, not to the user.
- 2026-05-25: User's name is Женя; address them as Женя when a name is appropriate.

- 2026-05-26: Saved the current responsive 3D site version as a separate local baseline copy at `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_saved_responsive_2026-05-26`. Use this folder as the preserved reference for the completed `Youjin-led/3d-form-2` version; future alternate 3D scene versions should be created in a different folder/repo so this baseline is not changed.

- 2026-05-26: For the jellyfish/card replacement, the user rejected procedural or primitive-built jellyfish. Use real imported/downloaded 3D assets for this direction, like the NIH spine source workflow, and keep source/provenance recorded.

- 2026-05-26: Active jellyfish work copy path to remember: `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2`. Preserved reference/baseline path: `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_saved_responsive_2026-05-26`.

- 2026-05-26: For this jellyfish scene, prefer Blender-baked GLB animation for bell contraction and tentacle motion. The site should play exported clips with `THREE.AnimationMixer`; browser code may control route movement and top-zone clip weight, but should not hand-deform the jellyfish body.

- 2026-05-26: For 3D/animation work, do not jump straight into implementation from vague taste words. First independently gather real-world motion references, quality 3D/model references, and candidate assets; reject weak/static/mismatched assets before importing; show 2-3 viable directions with tradeoffs; only then integrate into the site. User explicitly wants Codex to do this research/curation autonomously. --tags 3d,animation,workflow,preference

- 2026-05-26: For 3D asset work, use Hugging Face as a useful research/prototyping source when appropriate: Hunyuan3D, TRELLIS/TRELLIS 2, TripoSR/Stable Fast 3D, SAM 3D Objects, and related image-to-3D/text-to-3D Spaces can help create or compare static forms/GLB prototypes. Do not assume HF outputs production-ready rigged animation; final animation still needs Blender rig/shape keys or a real animated asset. --tags 3d,huggingface,tools,workflow

- 2026-05-27: For 3D/animation work, use GitHub as a source of tools and pipelines, not just assets. Useful directions to consider: 3DAIGC-API collections for TRELLIS/Hunyuan3D/UniRig/mesh painting, facebookresearch/actionmesh for video-to-animated-mesh research, sharpen3d/openvat for Blender vertex animation texture baking, and Blender-to-Three.js glTF export guides. Use these during research/curation before implementing. --tags 3d,github,animation,tools,workflow

- 2026-05-27: For long-running work, prevent Windows sleep only temporarily while Codex is actively working, preferably via a keep-awake process/API rather than permanent power-plan changes. Stop/release it after the task completes. Ask/notify before enabling when appropriate. --tags windows,power,long-running,workflow

- 2026-05-27: ZnakVsem marketplace MVP preference: make it feel like an extra PatentVsem tab, route all leads back to PatentVsem, hide trademark owner contacts, no user account, no online payment, staff-only admin, starter data from the first 30 signs on https://patentvsem.ru/tovarniy-znak, MKTU descriptions supplied by the user later, search via RU/EN transliteration. --tags znakvsem,patentvsem,requirements,preference

- 2026-05-27: Active Youjin-led/3d-form-3 work copy moved out of OneDrive to `C:\work\3d-form-3` to reduce file locking and slowdowns with large GLB/Blender/browser checks. Remote origin points to https://github.com/Youjin-led/3d-form-3.git. Prefer this path for future jellyfish/spine site work; old OneDrive path `C:\Users\Ардор\OneDrive\Рабочий стол\3d-form-2_work_v2` should be treated as legacy unless the user explicitly asks for it. --tags 3d-form-3,path,workflow,performance

- 2026-05-31: Self-improvement pass: before substantial work, use the project "Agent Operating Loop" pattern: orient to the correct project/work copy, search memory and patterns, choose roles/checkpoint based on risk, implement narrowly, run relevant QA, and log durable lessons. --tags agent,workflow,memory,qa,preference

- 2026-05-31: agent self-improvement pass: Repaired durable memory encoding damage, added the Agent Operating Loop pattern, linked it from project rules and patterns, synced markdown memory to SQLite, and verified agent/tool checks. Checks: npm run agent:status; npm run agent:evals; npm run check:tools.

- 2026-05-31: Project organization pass: completed project folders were collected under `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex`. Current `3d-form-3` path is now `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\3D\3d-form-3`; previous `C:\work\3d-form-3` was moved. Client sites are under `Проекты Codex\Клиентские сайты`; PatentVsem/ZnakVsem source materials are under `Проекты Codex\Материалы\patentvsem-znakvsem`. --tags organization,path,3d-form-3,client-sites

- 2026-05-31: organize completed projects: Collected completed 3D projects, client sites, and PatentVsem/ZnakVsem materials into C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex; moved 3d-form-3 from C:\work; deleted temporary browser profiles and QA screenshot archive; removed empty source folders. Checks: npm run agent:status; npm run agent:evals.

- 2026-05-31: Iskra agent center: safe copies of project agent memory/rules/tools/patterns/evals/checkpoints and a secret-free global Codex index were collected under `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\Искра`. Live workspace remains `C:\Users\Ардор\OneDrive\Рабочий стол\JS\ДЗ-1`; do not move it while active because npm scripts and current session depend on it. --tags iskra,agent,organization,path,memory

- 2026-05-31: collect Iskra agent center: Created C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\Искра with safe copies of project agent memory, rules, tools, patterns, evals, checkpoints, SQLite memory, and a secret-free global Codex index; excluded auth, sessions, sandbox secrets, logs/state databases, and caches. Checks: npm run agent:status; npm run agent:evals.

- 2026-05-31: External 3D artist workflow is part of Iskra's working context. Source folder remains `C:\Users\Ардор\OneDrive\Рабочий стол\3д художник` because it contains ~1.77 GB of Blender/GLB/tool assets; `Проекты Codex\Искра\external-3d-artist` keeps key scripts, README/config, manifests, and handling rules without duplicating heavy assets. Use it for Blender MCP, Active Theory-like scene assets, NIH spine assets, and external modeling workflows. --tags iskra,3d-artist,blender,mcp,workflow,path

- 2026-05-31: index external 3d artist workflow: Added C:\Users\Ардор\OneDrive\Рабочий стол\3д художник to Iskra context as external-3d-artist with key Blender/MCP scripts, README/config, and manifests for heavy models/output; kept source folder in place because check:tools and MCP workflows depend on it. Checks: npm run check:tools; npm run agent:status.

- 2026-05-31: Project launch map: `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\START_HERE.md` is the new first entry point for all collected work. It maps 3D projects, client sites, materials, Iskra's agent center, the external `3д художник` workflow, and the live workspace `JS\ДЗ-1`. Avoid stale locations such as `C:\work\3d-form-3` and old `JS\ДЗ-1\сайты Игорька`; use the organized `Проекты Codex` paths instead. --tags organization,start-here,path,iskra

- 2026-05-31: Post-cleanup project smoke: after reorganizing, JavaScript syntax checks passed for `Проекты Codex\Клиентские сайты\birzha\app.js`, `znakvsem-marketplace\app.js`, `patentvsem-handmade\main.js`, and `Проекты Codex\3D\3d-form-3\main.js`. Non-browser asset checks confirmed expected HTML/CSS/JS files plus `3d-form-3\assets\scene.glb`; Puppeteer browser smoke was attempted but stalled around Chrome/Puppeteer launch in this session, so do a real browser/visual QA before judging final 3D canvas output. --tags qa,organization,3d-form-3,client-sites

- 2026-05-31: Project launch docs added: `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\LAUNCHERS.md` contains concrete run/check commands for collected projects; `PROJECT_PASSPORTS.md` contains statuses, purposes, key files, launch commands, and next steps. `START_HERE.md` and the collection README link to both. --tags organization,launchers,project-passports,path

- 2026-05-31: post cleanup launch map and smoke audit: Created START_HERE.md for the organized project collection, audited stale paths, ran JS syntax and asset/file smoke checks for collected projects, and recorded the Puppeteer launch limitation for future visual QA. Checks: node --check collected JS files; non-browser asset/file checks; npm run memory:db -- import-md; npm run agent:status; npm run agent:evals.

- 2026-05-31: project launchers and passports: Added LAUNCHERS.md and PROJECT_PASSPORTS.md to the organized project collection, linked them from START_HERE.md and README.md, and recorded project run commands, statuses, key files, and next steps. Checks: created LAUNCHERS.md; created PROJECT_PASSPORTS.md; npm run memory:db -- import-md; npm run agent:status; npm run agent:evals.

- 2026-05-31: Research workflow preference: regularly use GitHub and Hugging Face as learning sources for Iskra and project work, but treat them as research/intake sources first. Do not install dependencies, clone large repos, run unknown code, or download heavy HF models/assets without explicit approval. Distill useful ideas into `patterns/`, `tools/`, evals, manifests, and memory. --tags github,huggingface,research,workflow,safety

- 2026-05-31: github huggingface research workflow: Added a recurring GitHub + Hugging Face research loop for safe source intake, reviewed initial 3D/Blender/HF sources, and recorded safety rules for not cloning, installing, running unknown code, or downloading heavy models without approval. Checks: web research: GitHub Blender-to-Three.js guide; web research: Hugging Face 3D Spaces and model listings; npm run memory:db -- import-md; npm run agent:status; npm run agent:evals.

- 2026-06-04: Completed ZnakVsem/Birzha client site baseline. Source project: `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\Клиентские сайты\birzha`; remote: `https://github.com/Youjin-led/birzha.git`; domain/hosting: `znakvsem.ru` on NIC HCP. Treat this as the reference structure for similar static client sites: multipage static HTML (`index`, `catalog`, `mktu`, `faq`, `about`, `place`), one shared `styles.css`, one shared `app.js`, `assets/`, `robots.txt`, `sitemap.xml`, no backend until needed. For NIC HCP, public files must be inside the hosting public folder, which in this case is `znakvsem.ru/docs`; if files are unpacked one level above `docs`, the domain keeps showing "site not published", and if `assets/` is not inside `docs`, logo/card images render blank. Pre-publish checklist: `node --check app.js`; check local href/src assets; Puppeteer smoke desktop/mobile; catalog count/search smoke; MKTU/detail smoke; build zip with `index.html` at the intended public root; verify zip contents and test after extraction. --tags znakvsem,birzha,client-sites,nic,hosting,static-site,qa,baseline

- 2026-06-06: Candle site navigation preference: keep the site multipage. Dropdown parent items open overview pages (wholesale.html, maker-goods.html); dropdown submenu items open separate category pages through category.html?section=...&item=...; dropdowns should close on outside click and Escape. --tags candles,client-sites,navigation,preference
