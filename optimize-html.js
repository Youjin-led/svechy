/**
 * Скрипт оптимизации HTML-файлов:
 * - Добавляет preconnect для Google Fonts
 * - Добавляет defer на main.js
 * - Убирает canvas со страниц, где он не нужен
 */
const fs = require('fs');
const path = require('path');

const files = [
  'admin.html', 'blog.html', 'calculator.html', 'cart.html',
  'category.html', 'contacts.html', 'index.html', 'maker-goods.html',
  'partners.html', 'reviews.html', 'wholesale.html'
];

const PREHEAD = `  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
`;

let count = 0;

for (const file of files) {
  const filePath = path.join(__dirname, file);
  if (!fs.existsSync(filePath)) {
    console.log(`⚠️ ${file} — не найден, пропускаю`);
    continue;
  }

  let html = fs.readFileSync(filePath, 'utf-8');

  // 1. Добавляем preconnect после favicon
  if (!html.includes('fonts.googleapis.com')) {
    html = html.replace(
      /<link rel="icon"[^>]*\/>/,
      (match) => `${match}\n${PREHEAD}`
    );
  }

  // 2. Добавляем defer на main.js
  html = html.replace(
    /<script src="main\.js"><\/script>/g,
    '<script src="main.js" defer></script>'
  );

  // 3. Убираем canvas со страниц, где он не нужен (все, кроме calculator.html)
  if (file !== 'calculator.html') {
    html = html.replace(
      /<canvas id="candleCanvas"[^>]*><\/canvas>/g,
      ''
    );
  }

  fs.writeFileSync(filePath, html, 'utf-8');
  count++;
  console.log(`✅ ${file} — обновлён`);
}

console.log(`\n✨ Обработано ${count} файлов`);
