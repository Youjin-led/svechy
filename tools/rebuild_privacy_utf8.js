const fs = require('fs');
const path = require('path');

const root = process.argv[2];
if (!root) {
  console.error('Usage: node tools/rebuild_privacy_utf8.js <site-root>');
  process.exit(1);
}

const html = `<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Политика обработки персональных данных - ПатентВсем</title>
    <meta name="description" content="Политика обработки персональных данных сайта биржи готовых товарных знаков ПатентВсем.">
    <link rel="stylesheet" href="styles.css?v=20260611-footer2">
  </head>
  <body>
    <header class="topbar">
      <a class="brand" href="index.html" aria-label="ПатентВсем">
        <img src="assets/patentvsem-logo.svg" alt="ПатентВсем">
      </a>
      <nav class="main-nav">
        <a href="about.html#how">Как это работает</a>
        <a href="about.html#team">Кто ведет сделку</a>
        <a href="mktu.html">МКТУ</a>
        <a href="catalog.html">Каталог</a>
        <a href="faq.html">FAQ</a>
        <a href="place.html">Разместить знак</a>
      </nav>
      <button class="header-cart" type="button" data-open-cart><span>Заявка</span><strong data-cart-count>0</strong></button>
    </header>
    <main>
      <section class="page-head">
        <p class="eyebrow">Персональные данные</p>
        <h1>Политика обработки персональных данных</h1>
        <p>Документ описывает, какие данные собирает сайт znakvsem.ru и как они используются при обработке заявок на покупку, консультацию или размещение товарного знака.</p>
      </section>
      <section class="content-panel legal-text">
        <article>
          <h2>1. Оператор</h2>
          <p>Оператором персональных данных является ИП Довлатов Игорь Мамедяревич.</p>
          <ul>
            <li>ИНН: 772612579857</li>
            <li>ОГРН/ОГРНИП: 319774600637982</li>
            <li>Патентное бюро: ПатентВсем</li>
            <li>Телефон: <a href="tel:+79689973835">89689973835</a></li>
            <li>Электронная почта: <a href="mailto:patentvsem@mail.ru">patentvsem@mail.ru</a></li>
          </ul>
        </article>
        <article>
          <h2>2. Какие данные обрабатываются</h2>
          <p>При отправке формы сайт может получать имя, телефон, электронную почту, комментарий к заявке, выбранные товарные знаки, технические данные браузера, страницу отправки и cookie-согласие.</p>
        </article>
        <article>
          <h2>3. Цели обработки</h2>
          <p>Данные используются для связи с пользователем, подготовки консультации, подбора товарного знака, сопровождения сделки и выполнения требований законодательства о персональных данных.</p>
          <p>Заявки с сайта могут передаваться в патентное бюро ПатентВсем и использоваться только для обработки обращения пользователя. Доступ к данным предоставляется сотрудникам и подрядчикам, которым он необходим для обработки заявки и сопровождения сделки.</p>
        </article>
        <article>
          <h2>4. Cookie</h2>
          <p>Сайт использует cookie для сохранения согласия пользователя, корзины заявок, избранных знаков и технических параметров посещения. Пользователь может ограничить cookie в настройках браузера.</p>
        </article>
        <article>
          <h2>5. Срок хранения и отзыв согласия</h2>
          <p>Данные хранятся в течение срока, необходимого для обработки обращения и исполнения юридических обязанностей. Пользователь может направить запрос на удаление или уточнение данных на адрес <a href="mailto:patentvsem@mail.ru">patentvsem@mail.ru</a>.</p>
        </article>
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
        <div><span>Персональные данные</span><a href="privacy.html">Политика обработки</a></div>
      </div>
    </footer>
    <script src="app.js?v=20260611-livefix1"></script>
  </body>
</html>
`;

fs.writeFileSync(path.join(root, 'privacy.html'), html, 'utf8');
console.log('Rebuilt privacy.html');
