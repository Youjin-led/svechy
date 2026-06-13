const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "commercial_buyer_package_casino_mirror_FIXED");
const ASSETS = path.join(OUT, "assets");

const num = (n) => new Intl.NumberFormat("ru-RU").format(n);
const rub = (n) => `${num(n)} ₽`;
const range = (a, b) => `${num(a)}-${num(b)} ₽`;

const copyIfExists = (from, to) => {
  if (fs.existsSync(from)) {
    fs.copyFileSync(from, to);
    return true;
  }
  return false;
};

const csv = (rows) =>
  rows
    .map((row) =>
      row
        .map((cell) => {
          const value = String(cell ?? "");
          return /[",\n;]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value;
        })
        .join(";")
    )
    .join("\n");

const costRows = [
  {
    section: "Материалы и производство",
    item: "Зеркала и стекло",
    min: 120000,
    real: 170000,
    max: 220000,
    why:
      "Переднее полупрозрачное зеркало, заднее зеркало, боковые зеркальные стенки, обработка кромок, риск боя на большом формате.",
  },
  {
    section: "Материалы и производство",
    item: "Силовой короб и рама",
    min: 60000,
    real: 90000,
    max: 120000,
    why:
      "Жесткий корпус глубиной 235 мм под размер 2125 x 1850 мм, посадочные места под зеркала, крепеж, сервисный доступ.",
  },
  {
    section: "Материалы и производство",
    item: "МДФ-заготовки и раскрой",
    min: 35000,
    real: 52000,
    max: 70000,
    why:
      "Карты, фишки, жетоны, масти и ромбы режутся отдельно, с подготовкой к покраске и креплению внутри короба.",
  },
  {
    section: "Материалы и производство",
    item: "LED и электрика",
    min: 35000,
    real: 55000,
    max: 75000,
    why:
      "Лента, блок питания, контроллер, провода, пайка, каналы обслуживания, тест на нагрев и стабильность.",
  },
  {
    section: "Материалы и производство",
    item: "Краски, лак, крепеж, расходники",
    min: 25000,
    real: 40000,
    max: 55000,
    why:
      "Грунт, металлики, лак, клеи, дистанционные элементы, крепеж, расходные материалы под ручную отделку.",
  },
  {
    section: "Материалы и производство",
    item: "Упаковка, защита, логистика",
    min: 30000,
    real: 60000,
    max: 90000,
    why:
      "Изделие крупное, зеркальное и хрупкое; требуется защита поверхностей, вынос, перевозка и резерв на повреждения.",
  },
  {
    section: "Работы",
    item: "Проектирование и подготовка КД",
    min: 50000,
    real: 85000,
    max: 120000,
    why:
      "Перевод картинки в размеры, слои, чертежи, DXF/SVG-контуры, ведомости, согласование с производством.",
  },
  {
    section: "Работы",
    item: "Ручная роспись МДФ-объектов",
    min: 120000,
    real: 185000,
    max: 250000,
    why:
      "Карты, фишки и декоративные элементы имеют не типовую окраску, а художественную отделку под казино и золото.",
  },
  {
    section: "Работы",
    item: "Сборка и юстировка зеркального эффекта",
    min: 80000,
    real: 120000,
    max: 160000,
    why:
      "Нужно собрать слои без перекосов, выставить отражения, убрать паразитные зазоры и сохранить доступ к сервису.",
  },
  {
    section: "Работы",
    item: "Электромонтаж и тесты",
    min: 25000,
    real: 42000,
    max: 60000,
    why:
      "Подключение, пайка, проверка питания, тест на нагрев, проверка сценария света до передачи клиенту.",
  },
  {
    section: "Работы",
    item: "Финальная проверка и переделки",
    min: 40000,
    real: 70000,
    max: 100000,
    why:
      "Контроль внешнего вида, чистка зеркал изнутри, исправление мелких дефектов, гарантийный запас времени.",
  },
];

const workRows = [
  ["Что оплачивает клиент", "Что реально делается", "Почему это отдельная работа"],
  [
    "Инженерная подготовка",
    "Размеры, слои, разрезы, раскрой, посадочные зоны, схема LED, согласование с цехом.",
    "Без этого изделие будет красивой картинкой, но не собираемой конструкцией.",
  ],
  [
    "Художественное изготовление объектов",
    "Карты, фишки, масти и ромбы вырезаются из МДФ, шлифуются, грунтуются, расписываются и лакируются.",
    "Главная ценность изделия в ручной детализации, а не только в листах зеркала.",
  ],
  [
    "Корпус и механика",
    "Делается жесткий короб 2125-2130 x 1850-1855 x 235 мм с пазами, крепежом и сервисным доступом.",
    "Большой формат требует жесткости: даже небольшой перекос портит отражение.",
  ],
  [
    "Зеркальный infinity-эффект",
    "Переднее one-way зеркало, заднее зеркало, боковые отражающие поверхности, дистанции и юстировка.",
    "Это оптическая система. Ее нельзя оценивать как обычную декоративную панель.",
  ],
  [
    "Свет и безопасность",
    "Подбор LED, блоков питания, контроллера, проводки, тест на нагрев и обслуживание.",
    "Покупатель платит за стабильную работу, а не за набор деталей.",
  ],
  [
    "Ответственность за результат",
    "Контроль качества, исправления, упаковка, риск боя, резерв на дефекты и гарантийные случаи.",
    "В штучном изделии часть цены - это защита клиента от переделок за его счет.",
  ],
];

const totals = {
  directMin: costRows.reduce((s, r) => s + r.min, 0),
  directReal: costRows.reduce((s, r) => s + r.real, 0),
  directMax: costRows.reduce((s, r) => s + r.max, 0),
  reserveMin: 70000,
  reserveReal: 95000,
  reserveMax: 120000,
  overheadMin: 60000,
  overheadReal: 80000,
  overheadMax: 100000,
  profitMin: 100000,
  profitReal: 140000,
  profitMax: 180000,
};

totals.saleMin = totals.directReal + totals.reserveMin + totals.overheadMin + totals.profitMin;
totals.saleReal = totals.directReal + totals.reserveReal + totals.overheadReal + totals.profitReal;
totals.saleMax = totals.directReal + totals.reserveMax + totals.overheadMax + totals.profitMax;

const md = `# Коммерческое обоснование цены

Проект: зеркальная световая инсталляция в стиле casino infinity mirror.

Габариты по текущему техпроекту: ширина 2125-2130 мм, высота 1850-1855 мм, глубина 235 мм.

Важно: это предварительная структура цены для объяснения покупателю. Это не публичная оферта и не финальная смета цеха. Финальная цена фиксируется после утверждения КД, материалов, крепления, доставки и места монтажа.

## Коротко для клиента

Это не обычное зеркало и не картина. Это крупная зеркальная световая инсталляция ручной работы: корпус, оптический тоннель, LED-система, зеркала большого формата и десятки декоративных объектов из МДФ с ручной росписью.

Ориентир честной себестоимости изделия: **${range(520000, 650000)}**.

Рекомендуемая цена продажи с резервом, организацией и ответственностью мастерской: **${range(750000, 950000)}**.

## На что уйдут деньги

| Блок | Реалистичный бюджет | Что внутри |
| --- | ---: | --- |
${costRows.map((r) => `| ${r.item} | ${rub(r.real)} | ${r.why} |`).join("\n")}

## Что именно оплачивает клиент как работу

${workRows
  .slice(1)
  .map((r) => `### ${r[0]}\n${r[1]}\n\nПочему это важно: ${r[2]}`)
  .join("\n\n")}

## Как объяснять цену без конфликта

Покупатель платит не за лист зеркала и не за набор лампочек. Он платит за готовый объект, который должен выглядеть дорого, ровно светиться, иметь глубину отражения, не развалиться при транспортировке и обслуживаться после установки.

Самая сильная формулировка: **"В цене есть материалы, ручная художественная работа, инженерная сборка, электрика, упаковка и ответственность за конечный результат."**

## Коммерческая модель

| Статья | Ориентир |
| --- | ---: |
| Прямая себестоимость материалов и работ | ${rub(totals.directReal)} |
| Резерв на бой, брак, переделки и гарантию | ${range(totals.reserveMin, totals.reserveMax)} |
| Накладные, закупки, организация производства | ${range(totals.overheadMin, totals.overheadMax)} |
| Прибыль мастерской | ${range(totals.profitMin, totals.profitMax)} |
| Рекомендуемая цена продажи | ${range(750000, 950000)} |

## Что можно вынести за рамки базовой цены

- Доставка и монтаж вне города.
- Сложный подвес, усиление стены, скрытая электрика.
- Премиальная фурнитура и спецстекло.
- Управление светом с телефона, несколько сценариев, диммирование по зонам.
- Срочное производство.
- Повторная переработка дизайна после утверждения макета.
`;

const readme = `# Commercial buyer package: casino infinity mirror

Папка собрана для разговора с покупателем. Она объясняет, из чего складывается себестоимость, какая работа оплачивается отдельно и почему продажная цена должна быть выше прямых затрат.

Открывать в первую очередь:

1. COMMERCIAL_EXPLANATION.pdf - понятное объяснение цены.
2. buyer_presentation_no_crop.pdf - короткая презентация для клиента, версия с необрезанной картинкой на слайде "Конструкция".
3. SEBESTOIMOST_BREAKDOWN.csv - таблица себестоимости.
4. RABOTY_I_OPLATA.csv - за что конкретно клиент платит как за работу.

Цифры являются предварительными. Для договора нужны финальная КД, согласованные материалы и расчет поставщиков.
`;

const html = `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Casino Infinity Mirror - коммерческое обоснование</title>
  <style>
    :root {
      --bg: #11100e;
      --paper: #f7f1e7;
      --ink: #231d17;
      --muted: #776b5c;
      --gold: #b88737;
      --red: #8f2530;
      --line: rgba(35,29,23,.18);
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Arial, Helvetica, sans-serif; background: var(--bg); color: var(--ink); }
    .deck { width: 1120px; margin: 0 auto; background: var(--paper); }
    section { min-height: 794px; padding: 54px 64px; border-bottom: 1px solid var(--line); page-break-after: always; position: relative; overflow: hidden; }
    h1, h2, h3 { margin: 0; line-height: 1.05; letter-spacing: 0; }
    h1 { font-size: 62px; max-width: 760px; }
    h2 { font-size: 42px; margin-bottom: 24px; }
    h3 { font-size: 22px; margin-bottom: 8px; }
    p { font-size: 21px; line-height: 1.45; margin: 0 0 16px; }
    .lead { font-size: 27px; max-width: 760px; color: #3b3026; }
    .kicker { color: var(--red); font-weight: 700; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 18px; font-size: 14px; }
    .hero { color: #fff; background: #050403; padding: 0; display: grid; grid-template-columns: 1fr 420px; }
    .hero .copy { padding: 56px 0 56px 64px; z-index: 1; }
    .hero h1, .hero p { color: #fff; text-shadow: 0 3px 24px #000; }
    .hero img { width: 100%; height: 794px; object-fit: cover; opacity: .88; }
    .price { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 34px; }
    .price div { background: #fff; color: var(--ink); border-left: 7px solid var(--gold); padding: 22px; min-height: 120px; }
    .price strong { display: block; font-size: 36px; margin-top: 10px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
    .card { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 18px; min-height: 150px; }
    .card b { display: block; font-size: 20px; margin-bottom: 8px; }
    .card span { color: var(--gold); font-size: 24px; font-weight: 800; }
    .card p { font-size: 15px; color: var(--muted); margin-top: 8px; }
    table { width: 100%; border-collapse: collapse; background: #fff; font-size: 16px; }
    th, td { border: 1px solid var(--line); padding: 11px 12px; vertical-align: top; }
    th { background: #2b241e; color: #fff; text-align: left; }
    td.money { text-align: right; white-space: nowrap; font-weight: 700; }
    .split { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; align-items: center; }
    .split.wide-visual { grid-template-columns: 1.18fr .82fr; gap: 34px; }
    .visual { width: 100%; border-radius: 8px; border: 1px solid var(--line); background: #120d09; }
    .visual.contain { height: 360px; object-fit: contain; padding: 12px; background: #0f1518; }
    .construction-diagram {
      height: 430px;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,.22);
      background: #101820;
      padding: 18px 22px 18px;
      position: relative;
      color: #fff;
      overflow: visible;
    }
    .legend-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 6px 10px;
      font-size: 11px;
      line-height: 1.15;
      color: #f6ead3;
      margin-bottom: 18px;
    }
    .legend-row b { color: #f7d875; }
    .depth-box {
      height: 230px;
      border: 3px solid #d9b45b;
      border-radius: 4px;
      position: relative;
      background: linear-gradient(90deg, rgba(111,183,210,.32), rgba(111,183,210,.12));
      margin-top: 8px;
    }
    .layer {
      position: absolute;
      top: -18px;
      bottom: -18px;
      width: 10px;
      border-radius: 2px;
      background: #f7d875;
      box-shadow: 0 0 0 2px rgba(255,255,255,.12);
    }
    .layer.front { left: 14px; background: #9fd7ee; }
    .layer.led { left: 80px; background: #ffcc55; }
    .layer.chips { left: 190px; background: #c99846; }
    .layer.cards { left: 300px; width: 16px; background: #f4df9a; }
    .layer.backlight { right: 120px; background: #f0a12a; }
    .layer.back { right: 16px; background: #9fd7ee; }
    .layer-label {
      position: absolute;
      top: 8px;
      left: 50%;
      transform: translateX(-50%);
      width: 24px;
      height: 24px;
      border-radius: 50%;
      font-size: 13px;
      line-height: 24px;
      color: #101820;
      background: #f7d875;
      font-weight: 800;
      text-align: center;
    }
    .front .layer-label,
    .led .layer-label,
    .chips .layer-label,
    .cards .layer-label,
    .backlight .layer-label,
    .back .layer-label { left: 50%; transform: translateX(-50%); }
    .depth-line {
      position: absolute;
      left: 14px;
      right: 14px;
      bottom: -34px;
      border-bottom: 2px solid #fff;
    }
    .depth-line::before,
    .depth-line::after {
      content: "";
      position: absolute;
      bottom: -6px;
      width: 0;
      height: 0;
      border-top: 6px solid transparent;
      border-bottom: 6px solid transparent;
    }
    .depth-line::before { left: -2px; border-right: 9px solid #fff; }
    .depth-line::after { right: -2px; border-left: 9px solid #fff; }
    .depth-text {
      position: absolute;
      left: 50%;
      bottom: -58px;
      transform: translateX(-50%);
      font-size: 20px;
      font-weight: 800;
      color: #fff;
    }
    .mini-card-shape {
      position: absolute;
      left: 270px;
      top: 72px;
      width: 128px;
      height: 70px;
      background: #f5d982;
      border-radius: 4px;
      transform: rotate(-8deg);
      color: #291e15;
      font-weight: 800;
      text-align: center;
      padding-top: 22px;
      box-shadow: 0 8px 18px rgba(0,0,0,.22);
    }
    .chip-dot {
      position: absolute;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      border: 6px solid #f5d982;
      background: #92212d;
      box-shadow: 0 0 20px rgba(245,216,130,.28);
    }
    .chip-dot.one { left: 145px; top: 82px; }
    .chip-dot.two { right: 82px; top: 134px; background: #251d18; }
    .chip-dot.three { left: 108px; bottom: 52px; background: #251d18; }
    .diagram-caption {
      position: absolute;
      left: 22px;
      bottom: 12px;
      font-size: 13px;
      color: #d6c7aa;
    }
    .big-number { font-size: 70px; color: var(--gold); font-weight: 800; line-height: .95; }
    .note { position: absolute; left: 64px; right: 64px; bottom: 34px; font-size: 14px; color: var(--muted); border-top: 1px solid var(--line); padding-top: 12px; }
    ul { margin: 0; padding-left: 22px; font-size: 21px; line-height: 1.5; }
    li { margin-bottom: 10px; }
    .dark { background: #18120d; color: #fff; }
    .dark h2, .dark p, .dark li { color: #fff; }
    .dark table { color: var(--ink); }
    @media print {
      body { background: #fff; }
      .deck { width: 1120px; }
      section { min-height: 794px; }
    }
  </style>
</head>
<body>
  <main class="deck">
    <section class="hero">
      <div class="copy">
        <div class="kicker">Коммерческое обоснование</div>
        <h1>Casino Infinity Mirror</h1>
        <p class="lead">Крупная зеркальная световая инсталляция ручной работы, а не обычное зеркало с подсветкой.</p>
        <div class="price">
          <div>Ориентир себестоимости<strong>${range(520000, 650000)}</strong></div>
          <div>Рекомендуемая цена продажи<strong>${range(750000, 950000)}</strong></div>
        </div>
      </div>
      <img src="assets/fasad.png" alt="Фасад композиции">
    </section>

    <section>
      <div class="kicker">Почему это стоит денег</div>
      <h2>Клиент покупает готовый эффект, а не отдельные детали</h2>
      <div class="split">
        <div>
          <p>Размер почти 2,13 x 1,85 м и глубина 23,5 см делают изделие инженерной конструкцией. Здесь важны жесткость короба, чистота зеркал, точная геометрия слоев, безопасная электрика и ручная художественная отделка.</p>
          <p>Главная мысль для продажи: в цене есть материалы, ручная работа, сборка, тесты, упаковка и ответственность за результат.</p>
        </div>
        <img class="visual" src="assets/model_front.png" alt="3D модель спереди">
      </div>
      <div class="note">Цифры предварительные: финальная смета фиксируется после КД, выбора материалов, способа монтажа и доставки.</div>
    </section>

    <section>
      <div class="kicker">Себестоимость</div>
      <h2>Куда уходят прямые затраты</h2>
      <div class="grid">
        ${costRows
          .slice(0, 6)
          .map(
            (r) => `<div class="card"><b>${r.item}</b><span>${rub(r.real)}</span><p>${r.why}</p></div>`
          )
          .join("")}
      </div>
      <div class="note">Материалы большого формата нельзя считать по цене маленького декора: зеркала, упаковка и риски боя резко увеличивают бюджет.</div>
    </section>

    <section>
      <div class="kicker">Работа мастерской</div>
      <h2>За какую работу платит клиент</h2>
      <table>
        <thead><tr><th>Работа</th><th>Реалистично</th><th>Что делается</th></tr></thead>
        <tbody>
          ${costRows
            .slice(6)
            .map((r) => `<tr><td>${r.item}</td><td class="money">${rub(r.real)}</td><td>${r.why}</td></tr>`)
            .join("")}
        </tbody>
      </table>
      <div class="note">Это штучное изделие. Большая часть ценности находится в проектировании, ручной отделке, юстировке и контроле качества.</div>
    </section>

    <section class="dark">
      <div class="kicker">Конструкция</div>
      <h2>Почему обычная смета “зеркало + LED” здесь неверна</h2>
      <div class="split wide-visual">
        <div class="construction-diagram" aria-label="Схема слоев по глубине">
          <div class="legend-row">
            <span><b>1</b> 0 мм: переднее one-way зеркало</span>
            <span><b>2</b> 20-35 мм: LED / мелкие масти</span>
            <span><b>3</b> 55-85 мм: фишки / жетоны</span>
            <span><b>4</b> 90-125 мм: МДФ-карты</span>
            <span><b>5</b> 150-190 мм: задний декор / свет</span>
            <span><b>6</b> 220-235 мм: заднее зеркало</span>
          </div>
          <div class="depth-box">
            <div class="layer front"><span class="layer-label">1</span></div>
            <div class="layer led"><span class="layer-label">2</span></div>
            <div class="layer chips"><span class="layer-label">3</span></div>
            <div class="layer cards"><span class="layer-label">4</span></div>
            <div class="layer backlight"><span class="layer-label">5</span></div>
            <div class="layer back"><span class="layer-label">6</span></div>
            <div class="mini-card-shape">МДФ-карты</div>
            <div class="chip-dot one"></div>
            <div class="chip-dot two"></div>
            <div class="chip-dot three"></div>
            <div class="depth-line"></div>
            <div class="depth-text">235 мм</div>
          </div>
          <div class="diagram-caption">Чистая схема слоев: все элементы видны полностью, без обрезки рендера.</div>
        </div>
        <ul>
          <li>Переднее полупрозрачное зеркало формирует глубину.</li>
          <li>Заднее и боковые зеркала создают многократное отражение.</li>
          <li>МДФ-объекты должны быть ровно размещены внутри слоя.</li>
          <li>LED должен светить эффектно, но не перегревать закрытый короб.</li>
          <li>Корпус должен выдержать вес и транспортировку.</li>
        </ul>
      </div>
    </section>

    <section>
      <div class="kicker">Цена продажи</div>
      <h2>Из чего складывается нормальная коммерческая цена</h2>
      <table>
        <thead><tr><th>Статья</th><th>Ориентир</th><th>Смысл для покупателя</th></tr></thead>
        <tbody>
          <tr><td>Прямая себестоимость</td><td class="money">${rub(totals.directReal)}</td><td>Материалы и фактическая работа по изготовлению.</td></tr>
          <tr><td>Резерв</td><td class="money">${range(totals.reserveMin, totals.reserveMax)}</td><td>Бой зеркал, переделки, гарантия, исправление дефектов.</td></tr>
          <tr><td>Накладные и организация</td><td class="money">${range(totals.overheadMin, totals.overheadMax)}</td><td>Закупки, логистика, координация цехов, упаковка процесса.</td></tr>
          <tr><td>Прибыль мастерской</td><td class="money">${range(totals.profitMin, totals.profitMax)}</td><td>Ответственность за проект и экономический смысл его делать.</td></tr>
          <tr><td><b>Рекомендуемая цена продажи</b></td><td class="money"><b>${range(750000, 950000)}</b></td><td><b>Цена готового результата, а не набора деталей.</b></td></tr>
        </tbody>
      </table>
    </section>

    <section>
      <div class="kicker">Формулировка для клиента</div>
      <h2>Как сказать просто</h2>
      <p class="lead">"Это изделие стоит дорого не потому, что в нем дорогая лампочка. Оно стоит так, потому что мы делаем большой зеркальный арт-объект: проектируем конструкцию, режем и красим десятки деталей, собираем оптический тоннель, подключаем свет, тестируем, упаковываем и отвечаем за результат."</p>
      <div class="split">
        <img class="visual" src="assets/section.png" alt="Разрез по глубине">
        <div>
          <div class="big-number">750-950 тыс.</div>
          <p>Рабочий коммерческий диапазон для качественного исполнения с запасом на риски, организацию и прибыль.</p>
        </div>
      </div>
      <div class="note">Что отдельно согласовать: доставка, монтаж, скрытая проводка, усиление стены, управление светом, сроки и гарантийные условия.</div>
    </section>
  </main>
</body>
</html>`;

const docHtml = `<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>Коммерческое обоснование цены</title>
  <style>
    body { font-family: Arial, Helvetica, sans-serif; color: #241f1a; margin: 42px; line-height: 1.45; }
    h1 { font-size: 34px; margin: 0 0 12px; }
    h2 { margin-top: 30px; font-size: 24px; }
    h3 { margin: 22px 0 6px; font-size: 18px; }
    p, li { font-size: 15px; }
    table { width: 100%; border-collapse: collapse; margin: 14px 0 24px; font-size: 12px; }
    th, td { border: 1px solid #c9bda9; padding: 8px; vertical-align: top; }
    th { background: #2b241e; color: #fff; text-align: left; }
    td:nth-child(2) { white-space: nowrap; text-align: right; font-weight: 700; }
    .box { background: #f5eddd; border-left: 5px solid #b88737; padding: 14px 16px; margin: 18px 0; }
  </style>
</head>
<body>
  <h1>Коммерческое обоснование цены</h1>
  <p><b>Проект:</b> зеркальная световая инсталляция Casino Infinity Mirror, 2125-2130 x 1850-1855 x 235 мм.</p>
  <div class="box"><b>Ориентир себестоимости:</b> ${range(520000, 650000)}<br><b>Рекомендуемая цена продажи:</b> ${range(750000, 950000)}</div>
  <p>Это предварительная структура цены для разговора с покупателем. Это не публичная оферта и не финальная смета цеха.</p>
  <h2>На что уйдут деньги</h2>
  <table><thead><tr><th>Блок</th><th>Реалистично</th><th>Что внутри</th></tr></thead><tbody>
    ${costRows.map((r) => `<tr><td>${r.item}</td><td>${rub(r.real)}</td><td>${r.why}</td></tr>`).join("")}
  </tbody></table>
  <h2>Что именно оплачивает клиент</h2>
  ${workRows.slice(1).map((r) => `<h3>${r[0]}</h3><p>${r[1]}</p><p><b>Почему это важно:</b> ${r[2]}</p>`).join("")}
  <h2>Как объяснять цену</h2>
  <p>Покупатель платит не за лист зеркала и не за набор лампочек. Он платит за готовый объект, который должен выглядеть дорого, ровно светиться, иметь глубину отражения, не развалиться при транспортировке и обслуживаться после установки.</p>
  <h2>Коммерческая модель</h2>
  <table><thead><tr><th>Статья</th><th>Ориентир</th><th>Комментарий</th></tr></thead><tbody>
    <tr><td>Прямая себестоимость материалов и работ</td><td>${rub(totals.directReal)}</td><td>Материалы и фактическая работа по изготовлению.</td></tr>
    <tr><td>Резерв на бой, брак, переделки и гарантию</td><td>${range(totals.reserveMin, totals.reserveMax)}</td><td>Защита клиента и мастерской от типовых рисков штучного зеркального изделия.</td></tr>
    <tr><td>Накладные, закупки, организация производства</td><td>${range(totals.overheadMin, totals.overheadMax)}</td><td>Координация поставщиков, закупки, логистика, контроль процесса.</td></tr>
    <tr><td>Прибыль мастерской</td><td>${range(totals.profitMin, totals.profitMax)}</td><td>Ответственность за проект и экономический смысл его делать.</td></tr>
    <tr><td><b>Рекомендуемая цена продажи</b></td><td><b>${range(750000, 950000)}</b></td><td><b>Цена готового результата.</b></td></tr>
  </tbody></table>
</body>
</html>`;

async function pdfFromHtml(input, output, opts = {}) {
  const puppeteer = require("puppeteer");
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();
  await page.goto(`file://${input.replace(/\\/g, "/")}`, { waitUntil: "networkidle0" });
  if (opts.screenshot) {
    await page.setViewport({ width: 1400, height: 900, deviceScaleFactor: 1 });
    if (opts.screenshotSection) {
      await page.evaluate((index) => {
        const section = document.querySelectorAll("section")[index];
        if (section) section.scrollIntoView();
      }, opts.screenshotSection);
    }
    await page.screenshot({ path: opts.screenshot, fullPage: false });
  }
  await page.pdf({
    path: output,
    printBackground: true,
    width: opts.width || "210mm",
    height: opts.height || "297mm",
    margin: opts.margin || { top: "12mm", right: "12mm", bottom: "12mm", left: "12mm" },
  });
  await browser.close();
}

async function main() {
  fs.rmSync(OUT, { recursive: true, force: true });
  fs.mkdirSync(ASSETS, { recursive: true });

  const assetMap = [
    ["чертежи/01_fasad_kompozicii.png", "fasad.png"],
    ["3d_model_dlya_konstruktora/preview_assembled_front.png", "model_front.png"],
    ["3d_model_dlya_konstruktora/preview_assembled_iso.png", "model_iso.png"],
    ["3d_model_dlya_konstruktora/preview_exploded_layers.png", "model_exploded.png"],
    ["чертежи_для_конструктора/02_razrez_po_glubine_i_sloi.png", "section.png"],
  ];
  const copied = assetMap.map(([from, to]) => copyIfExists(path.join(ROOT, from), path.join(ASSETS, to)));

  fs.writeFileSync(path.join(OUT, "README.md"), readme, "utf8");
  fs.writeFileSync(path.join(OUT, "COMMERCIAL_EXPLANATION.md"), md, "utf8");
  fs.writeFileSync(path.join(OUT, "COMMERCIAL_EXPLANATION.html"), docHtml, "utf8");
  fs.writeFileSync(path.join(OUT, "buyer_presentation.html"), html, "utf8");

  fs.writeFileSync(
    path.join(OUT, "SEBESTOIMOST_BREAKDOWN.csv"),
    "\ufeff" +
      csv([
        ["Раздел", "Позиция", "Минимум", "Реалистично", "Верхняя оценка", "Пояснение"],
        ...costRows.map((r) => [r.section, r.item, r.min, r.real, r.max, r.why]),
      ]),
    "utf8"
  );
  fs.writeFileSync(path.join(OUT, "RABOTY_I_OPLATA.csv"), "\ufeff" + csv(workRows), "utf8");

  await pdfFromHtml(path.join(OUT, "COMMERCIAL_EXPLANATION.html"), path.join(OUT, "COMMERCIAL_EXPLANATION.pdf"));
  await pdfFromHtml(path.join(OUT, "buyer_presentation.html"), path.join(OUT, "buyer_presentation_no_crop.pdf"), {
    width: "1120px",
    height: "794px",
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
    screenshot: path.join(OUT, "preview_buyer_slide_01.png"),
  });
  await pdfFromHtml(path.join(OUT, "buyer_presentation.html"), path.join(OUT, "buyer_presentation_construction_check.pdf"), {
    width: "1120px",
    height: "794px",
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
    screenshot: path.join(OUT, "preview_construction_slide_no_crop.png"),
    screenshotSection: 4,
  });

  console.log(JSON.stringify({ out: OUT, assetsCopied: copied.filter(Boolean).length, files: fs.readdirSync(OUT) }, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
