# Decisions

## 2026-06-03 - Start candle site as static atelier storefront

Decision: replace the current frontend surface with a dependency-free static candle website using `index.html`, `styles.css`, and `main.js`. The first version includes a product-first hero, canvas-generated candle visuals, responsive catalog filters, set presets, a local cart drawer, and a lead form.

Reason: the user asked to start a new candle website immediately and enable the project's existing tools/memory workflow. A static storefront gives a fast editable MVP without adding dependencies or waiting for product photography/CRM details.

## 2026-06-03 - Make candle site a calculator-first preorder interface

Decision: reshape the candle site around a color-palette visual and a compact preorder calculator instead of a classic shop/cart flow. The calculator builds a ready order text and routes it through Telegram share, WhatsApp text, email, or clipboard copy.

Reason: the user referenced `meliponini.ru/svechi` for the business essence, but asked for a simpler and more aesthetic interface with calculator and messenger/mail integration. The current static approach keeps the flow fast and usable while real contacts/CRM endpoints are still unknown.

## 2026-06-03 - Keep candle cards user-managed through local admin

Decision: remove prefilled public candle cards and add an in-page admin section that stores cards in `localStorage`. The public catalog is empty by default and only renders cards created through the admin form.

Reason: the user said cards should not be added yet and should be easy to add manually through an admin interface. Local browser storage is enough for the current static prototype; a real backend/CRM admin can replace it later.

## 2026-06-03 - Base candle site structure on Meliponini homepage

Decision: rebuild the candle site around the homepage structure observed on `meliponini.ru`: promo strip, navigation, hero, category directions, social strip, catalog, calculators, wholesale, about, admin/catalog management, contacts, and footer. Use the red/blue/wine/blush reference only as the color system.

Reason: the user clarified that the screenshot is only a palette reference, while the site structure should follow Meliponini's main site rather than the previous isolated calculator layout or a visual quadrants block.

## 2026-05-31 - Start trader app as paper trading terminal

Decision: build the first trader-app iteration as a local paper trading simulator with generated market data, visible strategy rules, stop-loss/take-profit, drawdown lock, and no real exchange API.

Reason: the user wants a trader that does not trade into losses, but profit cannot be guaranteed. A simulator makes the strategy inspectable and keeps real funds safe until backtesting and paper results are acceptable.

## 2026-05-31 - Keep agent upgrades project-local by default

Decision: improve the agent through project-local memory, patterns, tasks, and checks before editing global Codex skills or configuration.

Reason: project-local files are transparent, versionable, and already part of this workspace's workflow. Global `~/.codex/skills` changes are useful later, but they affect more than this project and should be done only when the user explicitly wants a reusable global skill.

## 2026-05-27 - ZnakVsem MVP scope

Decision: build `znakvsem.ru` as a PatentVsem-connected trademark catalog MVP, not as a standalone marketplace with user accounts or payments. The first release should include catalog cards, trademark detail pages, MKTU/discount/business filters, RU/EN transliteration search, favorites, a cart-like lead questionnaire, a "place trademark" request form, and a simple staff-only admin for adding/removing/editing signs.

Reason: the formal brief excludes personal accounts and payments, and the user clarified that all buyer leads must return to the existing PatentVsem lead flow. Trademark owners' contacts must stay hidden from buyers. Payments happen outside the site by manually generated QR/payment details.

## 2026-05-27 - ZnakVsem visual direction

Decision: prefer the PatentVsem style if feasible; otherwise use the older OnlineZnak layout patterns recolored and restyled closer to PatentVsem. The Yandex Disk archive of `onlineznak.ru_old_disign` is only a visual/layout reference, not the primary product source.

Reason: the user wants ZnakVsem to feel like an additional PatentVsem tab rather than an isolated Nikolai-style marketplace, while still preserving useful OnlineZnak catalog patterns.

## 2026-05-27 - ZnakVsem content source

Decision: use the first 30 trademark entries from `https://patentvsem.ru/tovarniy-znak` as starter catalog content. Each entry should keep its direct Rospatent link where available. MKTU descriptions will be provided by the user later.

Reason: the user explicitly chose PatentVsem's existing first 30 signs as the initial dataset, and PatentVsem already has direct Rospatent references.

## 2026-05-26 - Use Blender-built jellyfish for 3d-form-2 work copy

Decision: replace project cards in `3d-form-2_work_v2` with Blender-built jellyfish geometry exported in the scene GLB, while preserving `spiral_project_card_*_image` object names as movement/rail anchors.

Reason: the user explicitly wanted models like the spine pipeline rather than Three.js placeholders. Available external model sources required authentication/account flows for download, while Blender-built geometry allows immediate local iteration, exact palette matching, and no new licensing or dependency risk.

## 2026-05-25 - Keep PatentVsem rewrite static and isolated

Decision: build the Tilda rewrite as a dependency-free static site under `сайты Игорька/patentvsem-handmade/`, with handwritten HTML/CSS/JS and no Tilda UI runtime.

Reason: the user asked for a separate project that must not mix with the existing 3D work. The original site's lead routing is still Tilda-based, so forms temporarily post to the discovered Tilda endpoint/service ids until a dedicated backend or CRM integration is chosen.

## 2026-05-20 - Начать с markdown-памяти вместо векторной базы

Решение: использовать `AGENT_MEMORY.md`, `PROJECT_RULES.md`, `DECISIONS.md`, `EXPERIMENTS.md` и `TASKS.md` как первый слой внешней памяти.

Причина: это надежно, прозрачно, не требует сети и новых зависимостей. Векторную память можно добавить позже, когда появится стабильный набор заметок и понятный сценарий поиска.

## 2026-05-20 - Оставить существующий `npm run qa` как главный smoke-контур

Решение: опираться на уже имеющийся `qa_check.js`, который поднимает локальный сервер, открывает `index.html` через Puppeteer и проверяет diagnostics.

Причина: в проекте уже есть Puppeteer и Three.js, поэтому проверка визуальной сцены доступна без новой инфраструктуры.

## 2026-05-20 - Добавить SQLite-память без внешних зависимостей

Решение: создать `tools/agent_memory_db.py`, который хранит заметки в `.agent_memory.sqlite3` и использует SQLite FTS5 для поиска.

Причина: это дает более удобную локальную память с поиском и тегами, но не требует сетевой установки пакетов или отдельной базы данных.

## 2026-05-20 - Добавить команды контекста и логирования

Решение: создать `tools/agent_context.py` и `tools/agent_log.py`, подключив их как `npm run agent:context` и `npm run agent:log`.

Причина: агенту нужен быстрый способ восстановить состояние проекта и простой ритуал записи опыта после завершенных задач.

## 2026-05-20 - Добавить оркестрацию, checkpoints и активное управление памятью

Решение: добавить `AGENT_ROLES.md`, `PERMISSIONS.md`, `tools/agent_checkpoint.py`, `tools/agent_evals.py` и расширить SQLite-память полями `importance`, `access_count`, `last_accessed`, `archived`.

Причина: агент должен работать надежнее: разделять роли, сохранять слепки состояния, проверять себя eval-командой и не превращать память в свалку.

## 2026-05-20 - Разделить финальную сцену и черновые attempts

Решение: добавить `tools/scene_status.py` и `tools/scene_attempt.py`, подключив команды `scene:status` и `scene:attempt`.

Причина: промежуточные рендеры не должны смешиваться с текущей сценой. Финальным источником правды являются только `output/preview.png`, `output/scene.blend`, `output/scene.glb`.
## 2026-05-26 - Bake jellyfish body motion in Blender

Decision: jellyfish bell contraction and tentacle motion should be authored/exported in Blender as GLB animation clips, then played on the site with `THREE.AnimationMixer`.

Reason: the user rejected browser-procedural deformation for this direction and asked for animation to come from Blender/model assets, like the imported spine/model workflow. The site may still move the animated objects along its scene routes, but body motion belongs in the GLB.

## 2026-06-04 - Use the finished ZnakVsem site as the static client-site baseline

Decision: treat `Проекты Codex\Клиентские сайты\birzha` as the completed reference implementation for future small/medium static client sites that need a fast public launch on ordinary hosting.

Reason: this project established the practical end-to-end workflow: collect requirements from docs/screenshots, build a multipage static site, keep data inline or in simple assets when there is no backend, run browser QA before every visual claim, generate `robots.txt` and `sitemap.xml` for the real domain, package a clean hosting zip, and verify the actual hosting folder. For NIC HCP specifically, the public root may be `docs`; deploying above that folder leaves the host placeholder visible, and missing `docs/assets` produces blank logo/image frames.

## 2026-06-07 - Package the AI business idea as a standalone static project

Decision: create the new AI implementation business in `ai-business-project/` instead of modifying existing candle/static site files.

Reason: the user asked for a new business project. Keeping it isolated preserves existing client-site work, while still using the repo's local static-site pattern: plain HTML/CSS/JS, no new dependencies, documentation-first business artifacts, and browser QA screenshots.

## 2026-06-08 - Position the first sellable product as AI Monitor Studio

Decision: package the first commercial offer as `AI Monitor Studio` / `AI-мониторинг ресурсов под ключ`, with a simple pilot at 70 000 ₽ and regular monitoring at 120 000 ₽ setup plus 25 000 ₽/month support.

Reason: the user's first likely client needs a narrow, understandable service: collect information from selected internet resources and analyze it. Selling monitoring and reports is clearer than selling a generic AI bot or broad AI implementation.

## 2026-06-08 - Use a narrow first offer with a broader AI package catalog behind it

Decision: keep `AI-мониторинг + мини-база знаний` as the first market entry, but present it as one package inside a broader service catalog: monitoring, knowledge base, sales, documents, support, and management reports.

Reason: the business can technically solve many AI workflow tasks, but first sales convert better when the first offer is concrete. The catalog prevents the user from feeling boxed into one task and creates upsell paths after the first pilot.

## 2026-06-08 - Treat AI Monitor Studio as a company launch project, not only a demo

Decision: maintain a company-level blueprint under `ai-business-project/docs/` with launch roadmap, budget, checklist, resources, user tasks, and a visual map.

Reason: the user needs clarity on what to do next as a founder, not just more product screens. The business now has separate surfaces for product demo, sales site, internal outreach, service catalog, and company roadmap.

## 2026-06-08 - Split public sales site from internal sales workspace

Decision: keep `ai-business-project/sales-site/` as the clean public website for traffic and client trust, while `outreach-dashboard.html` remains an internal sales workspace and `research-assistant.html` remains the demo/product prototype.

Reason: the user needed clarity on what is sold versus what is used by the team. A public website should be simple and buyer-facing; the outreach dashboard contains working scripts/leads and should not be treated as the client product.

## 2026-06-08 - Make the client product surface a separate dashboard

Decision: create `ai-business-project/client-monitoring-app/` as the client-facing monitoring cabinet, separate from the public website, internal outreach workspace, and experimental research assistant.

Reason: the first sale needs a concrete product screen after the buyer asks "what exactly will I receive?" The dashboard makes the deliverable visible: sources, analysis run, report, risks, recommendations, mini knowledge base, and copied report.

## 2026-06-10 - Use a lightweight Node CMS for Svetlo admin features

Decision: implement Svetlo admin features with the existing `serve_static.js` Node server and a JSON store at `data/cms.json`, avoiding new dependencies for the first working admin MVP.

Reason: GitHub Pages can serve the static site but cannot securely write blog posts, reviews, product cards, or subsections. A small Node API keeps the admin workable locally and makes the future hosting requirement explicit.
