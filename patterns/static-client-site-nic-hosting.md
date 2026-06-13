# Static Client Site To NIC Hosting

Use this pattern for small client sites like ZnakVsem/Birzha: static pages, shared CSS/JS, simple catalog data, no backend at first, and deployment to ordinary hosting.

## Reference Baseline

- Completed project: `C:\Users\Ардор\OneDrive\Рабочий стол\Проекты Codex\Клиентские сайты\birzha`
- Remote: `https://github.com/Youjin-led/birzha.git`
- Domain example: `znakvsem.ru`
- Hosting lesson: on NIC HCP the public root can be `docs`, not the account/domain folder itself.

## Recommended Structure

```text
index.html
catalog.html
mktu.html
faq.html
about.html
place.html
app.js
styles.css
assets/
robots.txt
sitemap.xml
```

Keep the first release static unless a backend is truly required. For a catalog MVP, inline data in `app.js` is acceptable if the dataset is small enough and the owner/private contact table stays outside the public site.

## Build Workflow

1. Read the brief/docs/screenshots and extract a page map.
2. Build real pages, not a landing placeholder.
3. Keep visual style tied to the client's existing brand/reference.
4. Put reusable data/rendering logic in `app.js`; keep layout and theme in `styles.css`.
5. Add SEO basics for the final domain: titles, descriptions, `robots.txt`, `sitemap.xml`.
6. Before deploy, build a clean zip containing only public files.

## QA Before Publishing

- `node --check app.js`
- Check all local `href`/`src` references and `assets/` existence.
- Puppeteer desktop/mobile smoke for all pages.
- Functional smoke for catalog count, search/filter, cart/modal, and key forms.
- If there is an MKTU/FAQ/detail interaction, click at least one item and verify text appears.
- Extract the final zip into a temp folder and open the extracted version, not only the source folder.

## NIC HCP Deployment Notes

If the domain shows "Сайт не опубликован", the files are probably not in the hosting public root. In the ZnakVsem case the correct target was:

```text
/home/<account>/znakvsem.ru/docs/
```

Correct deployed structure:

```text
docs/index.html
docs/app.js
docs/styles.css
docs/assets/
```

Common failure modes:

- Files extracted to `/znakvsem.ru/` while the host serves `/znakvsem.ru/docs/`.
- `assets/` left one level above `docs`, causing blank logo/image frames.
- Archive extracted into an extra nested folder, causing `/docs/birzha-site-release/index.html` instead of `/docs/index.html`.
- Browser cache still showing the placeholder; use `Ctrl+F5` after fixing files.
