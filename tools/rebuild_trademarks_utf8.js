const fs = require('fs');
const path = require('path');

const root = process.argv[2];
if (!root) {
  console.error('Usage: node tools/rebuild_trademarks_utf8.js <site-root>');
  process.exit(1);
}

const appPath = path.join(root, 'app.js');
const app = fs.readFileSync(appPath, 'utf8');

function extractArray(source, marker) {
  const start = source.indexOf(marker);
  if (start === -1) throw new Error(`Marker not found: ${marker}`);
  const open = source.indexOf('[', start);
  let depth = 0;
  let inString = false;
  let quote = '';
  let escaped = false;
  for (let i = open; i < source.length; i += 1) {
    const ch = source[i];
    if (inString) {
      if (escaped) {
        escaped = false;
      } else if (ch === '\\') {
        escaped = true;
      } else if (ch === quote) {
        inString = false;
      }
    } else if (ch === '"' || ch === "'" || ch === '`') {
      inString = true;
      quote = ch;
    } else if (ch === '[') {
      depth += 1;
    } else if (ch === ']') {
      depth -= 1;
      if (depth === 0) return source.slice(open, i + 1);
    }
  }
  throw new Error(`Array not closed: ${marker}`);
}

const sourceTrademarks = Function(`return ${extractArray(app, 'const sourceTrademarks = [')}`)();
const registryBase = 'https://www1.fips.ru/registers-doc-view/fips_servlet?DB=RUTM&DocNumber=';

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function cleanLogoText(value) {
  return String(value || '')
    .replace(/изобразительный\s+товарный\s+знак/gi, '')
    .replace(/товарный\s+знак/gi, '')
    .replace(/знак\s+обслуживания/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function page(item) {
  const logo = cleanLogoText(item.logo || item.title || item.registryId || item.id) || `Знак №${item.registryId || item.id}`;
  const registryId = item.registryId || item.id;
  const registry = item.registry || `${registryBase}${encodeURIComponent(registryId)}&TypeFile=html`;
  const classes = Array.isArray(item.classes) ? item.classes.join(', ') : '';
  const business = Array.isArray(item.business) ? item.business.join(', ') : '';
  const price = item.price || 'по договоренности';
  const title = `Товарный знак ${logo} купить - ПатентВсем`;
  const description = `Готовый товарный знак ${logo}, регистрационный номер ${registryId}. Классы МКТУ: ${classes}. Цена: ${price}.`;
  return `<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${escapeHtml(title)}</title>
    <meta name="description" content="${escapeHtml(description)}">
    <link rel="canonical" href="https://znakvsem.ru/trademarks/${escapeHtml(item.id)}.html">
    <link rel="stylesheet" href="../styles.css?v=20260611-footer2">
  </head>
  <body>
    <header class="topbar">
      <a class="brand" href="../index.html" aria-label="ПатентВсем">
        <img src="../assets/patentvsem-logo.svg" alt="ПатентВсем">
      </a>
      <nav class="main-nav">
        <a href="../about.html#how">Как это работает</a>
        <a href="../about.html#team">Кто ведет сделку</a>
        <a href="../mktu.html">МКТУ</a>
        <a href="../catalog.html">Каталог</a>
        <a href="../faq.html">FAQ</a>
        <a href="../place.html">Разместить знак</a>
      </nav>
      <button class="header-cart" type="button" data-open-cart><span>Заявка</span><strong data-cart-count>0</strong></button>
    </header>
    <main>
      <section class="tm-detail-page">
        <div class="tm-detail-hero">
          <p class="eyebrow">Готовый товарный знак</p>
          <h1>${escapeHtml(logo)}</h1>
          <p>${escapeHtml(description)}</p>
          <div class="tm-detail-actions">
            <a class="button button-accent" href="../catalog.html?search=${encodeURIComponent(registryId)}">Открыть в каталоге</a>
            <a class="button button-ghost" href="${escapeHtml(registry)}" target="_blank" rel="noopener">Проверить в реестре</a>
          </div>
        </div>
        <dl class="tm-facts">
          <div><dt>Внутренний номер</dt><dd>№${escapeHtml(item.id)}</dd></div>
          <div><dt>Номер регистрации</dt><dd>${escapeHtml(registryId)}</dd></div>
          <div><dt>Классы МКТУ</dt><dd>${escapeHtml(classes || 'уточняются')}</dd></div>
          <div><dt>Направления</dt><dd>${escapeHtml(business || 'товары и услуги')}</dd></div>
          <div><dt>Стоимость</dt><dd>${escapeHtml(price)}</dd></div>
          <div><dt>Статус</dt><dd>Готов к проверке и передаче прав</dd></div>
        </dl>
      </section>
      <section class="seo-answer-block">
        <h2>Кому подходит товарный знак ${escapeHtml(logo)}</h2>
        <p>Лот можно рассматривать для бизнеса в направлениях: ${escapeHtml(business || 'товары и услуги')}. Перед покупкой ПатентВсем проверяет актуальность записи в реестре, классы МКТУ, правообладателя и условия передачи исключительного права.</p>
        <h2>Что проверить перед сделкой</h2>
        <ul>
          <li>соответствие классов МКТУ вашим товарам и услугам;</li>
          <li>актуальный статус знака в реестре Роспатента;</li>
          <li>условия договора отчуждения и сроки регистрации перехода права;</li>
          <li>возможность торга с текущим правообладателем.</li>
        </ul>
      </section>
    </main>
    <footer class="site-footer">
      <div class="footer-brand">
        <p class="eyebrow">Патентное бюро</p>
        <h2>ПатентВсем</h2>
        <span>Мы будем рады вас проконсультировать</span>
        <a href="tel:+79689973835">89689973835</a>
      </div>
      <div class="footer-details" aria-label="Реквизиты">
        <div><span>ИП</span><strong>Довлатов Игорь Мамедяревич</strong></div>
        <div><span>ИНН</span><strong>772612579857</strong></div>
        <div><span>ОГРН/ОГРНИП</span><strong>319774600637982</strong></div>
        <div><span>Электронная почта</span><a href="mailto:patentvsem@mail.ru">patentvsem@mail.ru</a></div>
        <div><span>Персональные данные</span><a href="../privacy.html">Политика обработки</a></div>
      </div>
    </footer>
    <script src="../app.js?v=20260611-livefix1"></script>
  </body>
</html>
`;
}

const outDir = path.join(root, 'trademarks');
fs.mkdirSync(outDir, { recursive: true });
for (const item of sourceTrademarks) {
  fs.writeFileSync(path.join(outDir, `${item.id}.html`), page(item), 'utf8');
}

console.log(`Rebuilt ${sourceTrademarks.length} trademark pages`);
