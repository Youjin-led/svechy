const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "чертежи_для_конструктора");
fs.mkdirSync(OUT, { recursive: true });

const W = 2130;
const H = 1850;
const D = 235;

function write(name, data) {
  fs.writeFileSync(path.join(OUT, name), data, "utf8");
}

function page(title, body, width = 1600, height = 1100) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}mm" height="${height}mm" viewBox="0 0 ${width} ${height}">
<defs>
  <marker id="arr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 Z" fill="#333"/>
  </marker>
  <marker id="arrGold" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 Z" fill="#c78020"/>
  </marker>
</defs>
<style>
  .border{fill:#fff;stroke:#111;stroke-width:1.5}
  .frame{fill:none;stroke:#111;stroke-width:3}
  .thin{fill:none;stroke:#666;stroke-width:1.2}
  .dash{fill:none;stroke:#777;stroke-width:1;stroke-dasharray:10 7}
  .dim{fill:none;stroke:#333;stroke-width:1.1;marker-start:url(#arr);marker-end:url(#arr)}
  .arrow{fill:none;stroke:#333;stroke-width:1.2;marker-end:url(#arr)}
  .mirror{fill:rgba(80,160,220,.18);stroke:#1476b8;stroke-width:2}
  .semi{fill:rgba(100,200,255,.10);stroke:#1476b8;stroke-width:2;stroke-dasharray:12 8}
  .mdf{fill:rgba(201,143,61,.18);stroke:#9b6118;stroke-width:2}
  .led{fill:none;stroke:#f29b22;stroke-width:4}
  .service{fill:rgba(80,180,90,.12);stroke:#2c8b3a;stroke-width:2}
  .warn{fill:#fff3cd;stroke:#b78300;stroke-width:1.5}
  text{font-family:Arial,sans-serif;fill:#111;letter-spacing:0}
  .title{font-size:26px;font-weight:700}
  .h{font-size:18px;font-weight:700}
  .t{font-size:15px}
  .s{font-size:12px}
  .stamp{font-size:11px}
</style>
<rect class="border" x="10" y="10" width="${width - 20}" height="${height - 20}"/>
<text class="title" x="32" y="44">${title}</text>
<rect class="warn" x="32" y="62" width="${width - 64}" height="34"/>
<text class="t" x="44" y="84">Схема для конструктора: показывает замысел, слои и требования. Не является финальным раскроем/КД.</text>
${body}
<rect x="${width - 340}" y="${height - 86}" width="310" height="58" fill="none" stroke="#111"/>
<text class="stamp" x="${width - 328}" y="${height - 64}">Casino infinity mirror</text>
<text class="stamp" x="${width - 328}" y="${height - 46}">Габарит 2130 x 1850 x 235 мм</text>
<text class="stamp" x="${width - 328}" y="${height - 28}">Лист для конструктора</text>
</svg>`;
}

function rr(x, y, w, h, r, cls = "thin") {
  return `<rect class="${cls}" x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}"/>`;
}

function dimH(x1, x2, y, label) {
  return `<line class="dim" x1="${x1}" y1="${y}" x2="${x2}" y2="${y}"/><text class="s" x="${(x1 + x2) / 2 - 32}" y="${y - 8}">${label}</text>`;
}

function dimV(x, y1, y2, label) {
  return `<line class="dim" x1="${x}" y1="${y1}" x2="${x}" y2="${y2}"/><text class="s" x="${x + 8}" y="${(y1 + y2) / 2}">${label}</text>`;
}

function card(x, y, rot, rank) {
  return `<g transform="translate(${x} ${y}) rotate(${rot})">
    <rect class="mdf" x="-58" y="-88" width="116" height="176" rx="8"/>
    <text class="s" x="-42" y="-54">${rank}</text>
  </g>`;
}

function chip(x, y, r, id) {
  return `<g><circle class="mdf" cx="${x}" cy="${y}" r="${r}"/><circle class="thin" cx="${x}" cy="${y}" r="${r * .55}"/><text class="s" x="${x + r + 5}" y="${y + 4}">${id}</text></g>`;
}

function sheet01() {
  const s = 0.42, ox = 95, oy = 120;
  const x = (v) => ox + v * s;
  const y = (v) => oy + v * s;
  const body = `
    ${rr(x(0), y(0), W * s, H * s, 145 * s, "frame")}
    ${rr(x(45), y(45), 2040 * s, 1760 * s, 112 * s, "led")}
    ${rr(x(190), y(170), 1750 * s, 1510 * s, 92 * s, "thin")}
    ${rr(x(455), y(390), 1220 * s, 1040 * s, 62 * s, "mirror")}
    ${dimH(x(0), x(W), y(H) + 42, "2130")}
    ${dimV(x(-85), y(0), y(H), "1850")}
    ${dimH(x(455), x(1675), y(360), "1220 центральная зона")}
    ${dimV(x(1705), y(390), y(1430), "1040")}
    ${card(x(740), y(360), -22, "10")}
    ${card(x(835), y(330), -14, "J")}
    ${card(x(930), y(305), -7, "J")}
    ${card(x(1030), y(285), 0, "Q")}
    ${card(x(1135), y(300), 8, "K")}
    ${card(x(1245), y(335), 18, "A")}
    ${chip(x(350), y(365), 31, "C1")}
    ${chip(x(425), y(650), 31, "C2")}
    ${chip(x(350), y(980), 31, "C3")}
    ${chip(x(365), y(1350), 31, "C4")}
    ${chip(x(1780), y(365), 31, "C5")}
    ${chip(x(1705), y(650), 31, "C6")}
    ${chip(x(1780), y(980), 31, "C7")}
    ${chip(x(1765), y(1350), 31, "C8")}
    <text class="h" x="1080" y="165">Что конструктор должен получить из листа</text>
    <text class="t" x="1080" y="205">1. Общий габарит и пропорции фасада.</text>
    <text class="t" x="1080" y="232">2. Где центральный зеркальный тоннель.</text>
    <text class="t" x="1080" y="259">3. Что реальные объекты ставятся один раз.</text>
    <text class="t" x="1080" y="286">4. Какие зоны нужны для LED-контуров.</text>
    <text class="t" x="1080" y="313">5. Что нужен отдельный рабочий разрез и узлы крепления.</text>
    <rect class="warn" x="1080" y="370" width="410" height="130"/>
    <text class="t" x="1100" y="400">Не резать по этому листу.</text>
    <text class="s" x="1100" y="428">Это карта компоновки. Рабочий чертеж</text>
    <text class="s" x="1100" y="448">должен уточнить пазы, толщины,</text>
    <text class="s" x="1100" y="468">крепеж, доступ и фактические размеры зеркал.</text>`;
  write("01_obschiy_vid_i_komponovka.svg", page("01 Общий вид и компоновка", body));
}

function sheet02() {
  const x0 = 130, y0 = 310, scale = 3.0;
  const layerX = (d) => x0 + d * scale;
  const body = `
    <text class="h" x="90" y="145">Разрез по глубине 235 мм</text>
    <rect class="frame" x="${x0}" y="${y0}" width="${D * scale}" height="360"/>
    <line class="dim" x1="${x0}" y1="${y0 + 410}" x2="${x0 + D * scale}" y2="${y0 + 410}"/><text class="t" x="${x0 + 315}" y="${y0 + 397}">235 мм</text>
    <rect class="semi" x="${layerX(0)}" y="${y0}" width="8" height="360"/><text class="s" x="${layerX(0) - 18}" y="${y0 - 18}">0: переднее полупрозрачное зеркало</text>
    <rect class="led" x="${layerX(25)}" y="${y0 + 20}" width="10" height="320"/><text class="s" x="${layerX(25) - 20}" y="${y0 - 42}">20-35: LED / мелкие масти</text>
    <rect class="mdf" x="${layerX(65)}" y="${y0 + 70}" width="22" height="220"/><text class="s" x="${layerX(65) - 20}" y="${y0 + 325}">55-85: фишки / жетоны</text>
    <rect class="mdf" x="${layerX(105)}" y="${y0 + 25}" width="24" height="310"/><text class="s" x="${layerX(105) - 35}" y="${y0 + 355}">90-125: карты</text>
    <rect class="led" x="${layerX(170)}" y="${y0 + 80}" width="12" height="200"/><text class="s" x="${layerX(155)}" y="${y0 - 18}">150-190: задний декор/свет</text>
    <rect class="mirror" x="${layerX(228)}" y="${y0}" width="12" height="360"/><text class="s" x="${layerX(198)}" y="${y0 - 42}">220-235: заднее зеркало</text>
    <text class="h" x="920" y="150">Задача конструктора</text>
    <text class="t" x="920" y="190">• назначить реальные зазоры;</text>
    <text class="t" x="920" y="220">• выбрать крепления MDF-деталей;</text>
    <text class="t" x="920" y="250">• сделать съемный/прижимной передний слой;</text>
    <text class="t" x="920" y="280">• предусмотреть сервис LED и БП;</text>
    <text class="t" x="920" y="310">• проверить отражения на макете.</text>
    <rect class="service" x="900" y="380" width="470" height="170"/>
    <text class="h" x="925" y="415">Сервисная зона</text>
    <text class="t" x="925" y="448">Нужен доступ к контроллеру и блоку питания.</text>
    <text class="t" x="925" y="476">Не закрывать БП без вентиляции.</text>
    <text class="t" x="925" y="504">Провода вести по зонам, не через видимое поле.</text>`;
  write("02_razrez_po_glubine_i_sloi.svg", page("02 Разрез по глубине и слои", body));
}

function sheet03() {
  const body = `
    <text class="h" x="80" y="150">Предлагаемая логика короба</text>
    <rect class="frame" x="90" y="200" width="520" height="650" rx="45"/>
    <rect class="mirror" x="145" y="255" width="410" height="540" rx="25"/>
    <text class="t" x="170" y="530">заднее зеркало / задняя панель</text>
    <rect class="semi" x="720" y="200" width="520" height="650" rx="45"/>
    <text class="t" x="830" y="530">переднее one-way зеркало</text>
    <line class="arrow" x1="650" y1="525" x2="705" y2="525"/>
    <text class="h" x="80" y="910">Требуемые узлы в рабочей КД</text>
    <text class="t" x="100" y="945">A. Силовая рама и задняя панель.</text>
    <text class="t" x="100" y="975">B. Посадочный паз/прижим переднего зеркала.</text>
    <text class="t" x="100" y="1005">C. Посадка заднего зеркала и боковых зеркал.</text>
    <text class="t" x="100" y="1035">D. Сервисный люк и вывод питания.</text>
    <text class="t" x="760" y="945">E. Механическое удержание стекла, не только клей.</text>
    <text class="t" x="760" y="975">F. Расчет веса и точки подвеса.</text>
    <text class="t" x="760" y="1005">G. Транспортная схема/ящик, если изделие везется целиком.</text>`;
  write("03_konstrukciya_koroba_i_uzly.svg", page("03 Конструкция короба и обязательные узлы", body));
}

function sheet04() {
  const body = `
    <text class="h" x="80" y="140">Предварительная ведомость деталей для конструктора</text>
    <foreignObject x="80" y="170" width="1380" height="760">
      <div xmlns="http://www.w3.org/1999/xhtml" style="font-family:Arial,sans-serif;font-size:20px">
        <table style="border-collapse:collapse;width:100%">
          <tr><th style="border:1px solid #333;padding:8px">Код</th><th style="border:1px solid #333;padding:8px">Деталь</th><th style="border:1px solid #333;padding:8px">Кол-во</th><th style="border:1px solid #333;padding:8px">Ориентир размера</th><th style="border:1px solid #333;padding:8px">Что уточнить</th></tr>
          <tr><td style="border:1px solid #333;padding:8px">M01</td><td style="border:1px solid #333;padding:8px">Переднее one-way зеркало</td><td style="border:1px solid #333;padding:8px">1</td><td style="border:1px solid #333;padding:8px">2110 x 1830</td><td style="border:1px solid #333;padding:8px">паз, кромка, съемность</td></tr>
          <tr><td style="border:1px solid #333;padding:8px">M02</td><td style="border:1px solid #333;padding:8px">Заднее зеркало</td><td style="border:1px solid #333;padding:8px">1</td><td style="border:1px solid #333;padding:8px">1950 x 1670</td><td style="border:1px solid #333;padding:8px">посадка, доступ</td></tr>
          <tr><td style="border:1px solid #333;padding:8px">M03-M06</td><td style="border:1px solid #333;padding:8px">Боковые зеркала глубины</td><td style="border:1px solid #333;padding:8px">4</td><td style="border:1px solid #333;padding:8px">1670/1950 x 235</td><td style="border:1px solid #333;padding:8px">стыки, углы, кромки</td></tr>
          <tr><td style="border:1px solid #333;padding:8px">K01-K06</td><td style="border:1px solid #333;padding:8px">Карты MDF</td><td style="border:1px solid #333;padding:8px">6</td><td style="border:1px solid #333;padding:8px">260 x 390</td><td style="border:1px solid #333;padding:8px">контур, крепеж, роспись</td></tr>
          <tr><td style="border:1px solid #333;padding:8px">C01-C08</td><td style="border:1px solid #333;padding:8px">Фишки MDF</td><td style="border:1px solid #333;padding:8px">8-10</td><td style="border:1px solid #333;padding:8px">D145</td><td style="border:1px solid #333;padding:8px">контур, крепеж</td></tr>
          <tr><td style="border:1px solid #333;padding:8px">LED</td><td style="border:1px solid #333;padding:8px">Подсветка</td><td style="border:1px solid #333;padding:8px">23-28 м</td><td style="border:1px solid #333;padding:8px">24V</td><td style="border:1px solid #333;padding:8px">мощность, зоны, доступ</td></tr>
        </table>
      </div>
    </foreignObject>
    <text class="h" x="80" y="985">Финальный комплект от конструктора должен включать:</text>
    <text class="t" x="100" y="1020">общий вид, разрезы, узлы, раскрой зеркал, раскрой MDF, схему LED, спецификацию крепежа, расчет веса.</text>`;
  write("04_vedomost_i_chto_dolzhen_sdelat_konstruktor.svg", page("04 Ведомость и задачи конструктора", body));
}

function buildHtmlPdfScript() {
  write("README.md", `# Чертежи для конструктора

Это не финальная рабочая КД и не раскрой для резки.

Назначение: дать конструктору понятную схему изделия:

- общий вид и компоновка;
- разрез по глубине 235 мм;
- логика короба и обязательные узлы;
- ведомость деталей и список задач конструктора.

Файлы:

- 01_obschiy_vid_i_komponovka.pdf
- 02_razrez_po_glubine_i_sloi.pdf
- 03_konstrukciya_koroba_i_uzly.pdf
- 04_vedomost_i_chto_dolzhen_sdelat_konstruktor.pdf

В работу конструктору отправлять вместе с папкой \`чертежи_ТЗ_для_производства\`.
`);
}

sheet01();
sheet02();
sheet03();
sheet04();
buildHtmlPdfScript();
console.log(OUT);
