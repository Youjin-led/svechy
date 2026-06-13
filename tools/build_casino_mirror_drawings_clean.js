const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, "чертежи");
fs.mkdirSync(OUT, { recursive: true });

const W = 2130;
const H = 1850;
const D = 235;

function write(name, data) {
  fs.writeFileSync(path.join(OUT, name), data, "utf8");
}

function sheet({ title, width = 2400, height = 1700, dark = false, body }) {
  const bg = dark ? "#080705" : "#ffffff";
  const fg = dark ? "#f7e7bd" : "#111";
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="${width}mm" height="${height}mm" viewBox="0 0 ${width} ${height}">
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
    <path d="M0,0 L8,4 L0,8 Z" fill="${dark ? "#f7c46a" : "#555"}"/>
  </marker>
  <radialGradient id="chipRed" cx="50%" cy="45%" r="60%">
    <stop offset="0%" stop-color="#ffcc79"/>
    <stop offset="40%" stop-color="#aa1610"/>
    <stop offset="100%" stop-color="#260604"/>
  </radialGradient>
  <radialGradient id="chipBlack" cx="50%" cy="45%" r="60%">
    <stop offset="0%" stop-color="#ffd890"/>
    <stop offset="42%" stop-color="#111"/>
    <stop offset="100%" stop-color="#040403"/>
  </radialGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  .bg{fill:${bg}}
  .frame{fill:none;stroke:#d58a25;stroke-width:5}
  .gold{fill:none;stroke:#d79b38;stroke-width:3}
  .thinGold{fill:none;stroke:#d79b38;stroke-width:1.4}
  .dim{fill:none;stroke:${dark ? "#f7c46a" : "#555"};stroke-width:1.2;marker-start:url(#arrow);marker-end:url(#arrow)}
  .guide{fill:none;stroke:${dark ? "rgba(255,215,120,.35)" : "#999"};stroke-width:.8;stroke-dasharray:12 8}
  .label{font-family:Arial,sans-serif;font-size:24px;fill:${fg}}
  .small{font-family:Arial,sans-serif;font-size:16px;fill:${fg}}
  .tiny{font-family:Arial,sans-serif;font-size:12px;fill:${fg}}
  .card{fill:#c69043;stroke:#2b1708;stroke-width:2}
  .cardLine{fill:none;stroke:#2b1708;stroke-width:2}
  .mirror{fill:${dark ? "rgba(30,90,125,.28)" : "rgba(110,180,220,.15)"};stroke:#53a9df;stroke-width:2}
  .mdf{fill:rgba(205,143,58,.16);stroke:#8f5b14;stroke-width:2}
  .cut{fill:none;stroke:#111;stroke-width:1.4}
  .engrave{fill:none;stroke:#1266a8;stroke-width:1;stroke-dasharray:9 6}
  text{letter-spacing:0}
</style>
<rect class="bg" x="0" y="0" width="${width}" height="${height}"/>
<text class="label" x="32" y="42">${title}</text>
${body}
<rect x="${width - 360}" y="${height - 110}" width="330" height="82" fill="none" stroke="${dark ? "#d79b38" : "#111"}"/>
<text class="small" x="${width - 342}" y="${height - 82}">Casino mirror composition</text>
<text class="tiny" x="${width - 342}" y="${height - 56}">Габарит: 2130 x 1850 x 235 мм</text>
<text class="tiny" x="${width - 342}" y="${height - 34}">Чистая версия по референсу</text>
</svg>`;
}

function roundedRect(x, y, w, h, r, cls = "gold") {
  return `<rect class="${cls}" x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}"/>`;
}

function card(x, y, rot, rank) {
  return `<g transform="translate(${x} ${y}) rotate(${rot})">
    <rect class="card" x="-130" y="-195" width="260" height="390" rx="16"/>
    <rect class="cardLine" x="-108" y="-170" width="216" height="340" rx="10"/>
    <text x="-104" y="-135" font-family="Georgia,serif" font-size="42" fill="#17100a">${rank}</text>
    <path fill="#17100a" d="M0,-52 C-62,12 -24,78 0,66 C24,78 62,12 0,-52 Z M0,66 L-24,122 L24,122 Z"/>
    <text x="80" y="152" font-family="Georgia,serif" font-size="36" fill="#17100a" transform="rotate(180 80 152)">${rank}</text>
  </g>`;
}

function chip(x, y, r, type, id) {
  const fill = type === "red" ? "url(#chipRed)" : "url(#chipBlack)";
  const wedges = Array.from({ length: 8 }, (_, i) => {
    const a = (i * 45 - 12) * Math.PI / 180;
    const x1 = x + Math.cos(a) * (r - 12);
    const y1 = y + Math.sin(a) * (r - 12);
    return `<circle cx="${x1.toFixed(1)}" cy="${y1.toFixed(1)}" r="${r * 0.095}" fill="#f4c06a"/>`;
  }).join("");
  return `<g>
    <circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="#e2aa4e" stroke-width="3"/>
    <circle cx="${x}" cy="${y}" r="${r * 0.58}" fill="none" stroke="#f1bb61" stroke-width="2"/>
    <circle cx="${x}" cy="${y}" r="${r * 0.25}" fill="rgba(255,210,120,.25)" stroke="#f1bb61" stroke-width="2"/>
    ${wedges}
    <text class="tiny" x="${x + r + 10}" y="${y + 4}">${id}</text>
  </g>`;
}

function token(x, y, id) {
  return `<g>
    <circle cx="${x}" cy="${y}" r="43" fill="rgba(232,168,63,.18)" stroke="#d79b38" stroke-width="2"/>
    <circle cx="${x}" cy="${y}" r="25" fill="none" stroke="#d79b38" stroke-width="1.4"/>
    <text class="tiny" x="${x + 50}" y="${y + 4}">${id}</text>
  </g>`;
}

function suitSymbol(x, y, s, type = "spade") {
  const paths = {
    spade: "M0,-28 C-34,6 -13,36 0,27 C13,36 34,6 0,-28 Z M0,27 L-13,54 L13,54 Z",
    club: "M-16,-5 A16,16 0 1 1 -1,-22 A16,16 0 1 1 16,-5 A16,16 0 1 1 8,20 L17,50 L-17,50 L-8,20 A16,16 0 1 1 -16,-5 Z",
    diamond: "M0,-34 L28,0 L0,34 L-28,0 Z",
    heart: "M0,31 C-38,-4 -29,-34 -7,-27 C-2,-25 0,-19 0,-19 C0,-19 2,-25 7,-27 C29,-34 38,-4 0,31 Z",
  };
  return `<path d="${paths[type]}" transform="translate(${x} ${y}) scale(${s})" fill="none" stroke="#d79b38" stroke-width="${2 / s}"/>`;
}

function frontComposition() {
  const ox = 135;
  const oy = 95;
  const scale = 0.72;
  const x = (v) => ox + v * scale;
  const y = (v) => oy + v * scale;
  const sw = W * scale;
  const sh = H * scale;
  const ledDots = [];
  for (let i = 0; i <= 34; i++) {
    const px = x(75 + i * (1980 / 34));
    ledDots.push(`<circle cx="${px}" cy="${y(55)}" r="5" fill="#ffb33e" filter="url(#glow)"/>`);
    ledDots.push(`<circle cx="${px}" cy="${y(1795)}" r="5" fill="#ffb33e" filter="url(#glow)"/>`);
  }
  for (let i = 0; i <= 26; i++) {
    const py = y(95 + i * (1660 / 26));
    ledDots.push(`<circle cx="${x(55)}" cy="${py}" r="5" fill="#ffb33e" filter="url(#glow)"/>`);
    ledDots.push(`<circle cx="${x(2075)}" cy="${py}" r="5" fill="#ffb33e" filter="url(#glow)"/>`);
  }

  const chips = [
    [350, 365, "red", "C1"], [425, 650, "black", "C2"], [350, 980, "red", "C3"], [365, 1350, "black", "C4"],
    [1780, 365, "black", "C5"], [1705, 650, "red", "C6"], [1780, 980, "black", "C7"], [1765, 1350, "red", "C8"],
  ].map(([cx, cy, type, id]) => chip(x(cx), y(cy), 72.5 * scale, type, id)).join("");
  const tokens = [
    [360, 515, "T1"], [420, 810, "T2"], [370, 1165, "T3"], [300, 1510, "T4"],
    [1770, 515, "T5"], [1710, 810, "T6"], [1760, 1165, "T7"], [1830, 1510, "T8"],
    [620, 1280, "T9"], [1510, 1280, "T10"], [760, 575, "T11"], [1370, 575, "T12"],
  ].map(([cx, cy, id]) => token(x(cx), y(cy), id)).join("");
  const cards = [
    [740, 360, -22, "10"], [835, 330, -14, "J"], [930, 305, -7, "J"], [1030, 285, 0, "Q"], [1135, 300, 8, "K"], [1245, 335, 18, "A"],
  ].map(([cx, cy, rot, rank]) => card(x(cx), y(cy), rot, rank)).join("");
  const suits = [
    [280, 1600, "club"], [520, 1600, "spade"], [840, 1600, "diamond"], [1065, 1600, "spade"], [1290, 1600, "heart"], [1610, 1600, "club"], [1850, 1600, "spade"],
    [300, 255, "club"], [1830, 255, "spade"], [540, 250, "diamond"], [1590, 250, "heart"],
  ].map(([cx, cy, type]) => suitSymbol(x(cx), y(cy), 0.72, type)).join("");

  const body = `
    <g>
      ${roundedRect(x(0), y(0), sw, sh, 145 * scale, "frame")}
      ${roundedRect(x(45), y(45), 2040 * scale, 1760 * scale, 112 * scale, "gold")}
      ${roundedRect(x(190), y(170), 1750 * scale, 1510 * scale, 92 * scale, "thinGold")}
      ${roundedRect(x(455), y(390), 1220 * scale, 1040 * scale, 62 * scale, "mirror")}
      ${ledDots.join("")}
      ${suits}
      ${chips}
      ${tokens}
      ${cards}
      <line class="dim" x1="${x(0)}" y1="${y(1888)}" x2="${x(W)}" y2="${y(1888)}"/><text class="small" x="${x(980)}" y="${y(1938)}">2130 мм</text>
      <line class="dim" x1="${x(-70)}" y1="${y(0)}" x2="${x(-70)}" y2="${y(H)}"/><text class="small" x="${x(-145)}" y="${y(930)}">1850 мм</text>
      <line class="dim" x1="${x(455)}" y1="${y(360)}" x2="${x(1675)}" y2="${y(360)}"/><text class="tiny" x="${x(940)}" y="${y(340)}">центральное зеркало 1220 мм</text>
      <text class="small" x="${x(470)}" y="${y(1460)}">центральная зона отражения / infinity mirror</text>
      <text class="small" x="${x(690)}" y="${y(730)}">реальный MDF-веер карт 6 шт.</text>
      <text class="small" x="${x(80)}" y="${y(1820)}">Реальные объекты считаются один раз. Глубина создается зеркалами.</text>
    </g>`;
  write("01_fasad_kompozicii.svg", sheet({ title: "01 Фасад композиции по референсу", width: 1800, height: 1550, dark: true, body }));
}

function mirrorSheet() {
  const body = `
    <rect class="mirror" x="45" y="90" width="1055" height="915"/><text class="small" x="45" y="75">M01 переднее полупрозрачное зеркало 2110 x 1830</text>
    <rect class="mirror" x="1160" y="130" width="975" height="835"/><text class="small" x="1160" y="115">M02 заднее зеркало 1950 x 1670</text>
    <rect class="mirror" x="45" y="1120" width="835" height="118"/><text class="small" x="45" y="1100">M03/M04 боковые зеркала 1670 x 235, 2 шт.</text>
    <rect class="mirror" x="940" y="1120" width="975" height="118"/><text class="small" x="940" y="1100">M05/M06 верх/низ 1950 x 235, 2 шт.</text>
    <text class="label" x="45" y="1345">Важно: размеры зеркал финализировать после готового короба и посадочных пазов.</text>`;
  write("02_raskroy_zerkal.svg", sheet({ title: "02 Раскрой зеркал", width: 2200, height: 1450, body }));
}

function mdfSheets() {
  const cards = Array.from({ length: 6 }, (_, i) => {
    const x = 45 + i * 305;
    const rank = ["10", "J", "J", "Q", "K", "A"][i];
    return `<g><rect class="cut" x="${x}" y="105" width="260" height="390" rx="16"/><rect class="engrave" x="${x + 18}" y="123" width="224" height="354" rx="10"/><text class="label" x="${x + 24}" y="164">${rank}</text><path class="engrave" d="M ${x + 130} 225 C ${x + 70} 285 ${x + 104} 345 ${x + 130} 340 C ${x + 156} 345 ${x + 190} 285 ${x + 130} 225 Z M ${x + 130} 340 L ${x + 106} 390 L ${x + 154} 390 Z"/></g>`;
  }).join("");
  write("03_mdf_karty_260x390.svg", sheet({ title: "03 MDF карты: 6 шт. 260 x 390 мм", width: 1920, height: 620, body: cards }));

  const chips = Array.from({ length: 10 }, (_, i) => {
    const x = 100 + (i % 5) * 190;
    const y = 130 + Math.floor(i / 5) * 190;
    return `<g><circle class="cut" cx="${x}" cy="${y}" r="72.5"/><circle class="engrave" cx="${x}" cy="${y}" r="43"/><circle class="engrave" cx="${x}" cy="${y}" r="22"/><text class="tiny" x="${x - 25}" y="${y + 5}">D145</text></g>`;
  }).join("");
  const tokens = Array.from({ length: 14 }, (_, i) => {
    const x = 80 + (i % 7) * 130;
    const y = 540 + Math.floor(i / 7) * 110;
    return `<g><circle class="cut" cx="${x}" cy="${y}" r="42.5"/><circle class="engrave" cx="${x}" cy="${y}" r="24"/><text class="tiny" x="${x - 20}" y="${y + 5}">D85</text></g>`;
  }).join("");
  const suits = ["spade", "club", "diamond", "heart"].flatMap((type, row) =>
    Array.from({ length: row < 2 ? 10 : 8 }, (_, i) => suitSymbol(1050 + i * 82, 140 + row * 100, 0.75, type))
  ).join("");
  write("04_mdf_fishki_zhetony_masti.svg", sheet({ title: "04 MDF фишки, жетоны, масти", width: 1920, height: 760, body: chips + tokens + suits }));
}

function ledSheet() {
  const sx = 0.62;
  const ox = 80;
  const oy = 80;
  const x = (v) => ox + v * sx;
  const y = (v) => oy + v * sx;
  const body = `
    ${roundedRect(x(0), y(0), W * sx, H * sx, 145 * sx, "cut")}
    ${roundedRect(x(45), y(45), 2040 * sx, 1760 * sx, 112 * sx, "gold")}
    ${roundedRect(x(190), y(170), 1750 * sx, 1510 * sx, 92 * sx, "gold")}
    ${roundedRect(x(455), y(390), 1220 * sx, 1040 * sx, 62 * sx, "gold")}
    <text class="label" x="${x(90)}" y="${y(120)}">A внешний контур: ~7.6 м</text>
    <text class="label" x="${x(260)}" y="${y(245)}">B внутренний контур: ~6.1 м</text>
    <text class="label" x="${x(540)}" y="${y(470)}">C тоннель: ~4.5 м</text>
    <text class="label" x="${x(90)}" y="${y(1780)}">D вертикальные/декор-линии: 5–8 м. Итого LED: 23–28 м с запасом.</text>
    <rect x="1540" y="260" width="230" height="95" fill="none" stroke="#111"/><text class="label" x="1570" y="315">контроллер</text>
    <rect x="1540" y="405" width="230" height="95" fill="none" stroke="#111"/><text class="label" x="1570" y="460">БП 24V</text>
    <line class="dim" x1="1655" y1="355" x2="1655" y2="405"/>
    <text class="small" x="1450" y="560">Рекомендация: 24V, 2–3 зоны питания, запас мощности 25–30%.</text>`;
  write("05_led_shema.svg", sheet({ title: "05 Схема LED-подключения", width: 1850, height: 1350, body }));
}

function dxfHeader() {
  return "0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1027\n0\nENDSEC\n0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n0\nLAYER\n2\nCUT\n70\n0\n62\n1\n6\nCONTINUOUS\n0\nLAYER\n2\nENGRAVE\n70\n0\n62\n5\n6\nCONTINUOUS\n0\nLAYER\n2\nTEXT\n70\n0\n62\n7\n6\nCONTINUOUS\n0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n";
}
const dxfFooter = "0\nENDSEC\n0\nEOF\n";
const line = (x1, y1, x2, y2, layer = "CUT") => `0\nLINE\n8\n${layer}\n10\n${x1}\n20\n${y1}\n30\n0\n11\n${x2}\n21\n${y2}\n31\n0\n`;
const circleDxf = (x, y, r, layer = "CUT") => `0\nCIRCLE\n8\n${layer}\n10\n${x}\n20\n${y}\n30\n0\n40\n${r}\n`;
function rectDxf(x, y, w, h, layer = "CUT") {
  return line(x, y, x + w, y, layer) + line(x + w, y, x + w, y + h, layer) + line(x + w, y + h, x, y + h, layer) + line(x, y + h, x, y, layer);
}
function dxfFiles() {
  const mirror = [
    rectDxf(0, 0, 2110, 1830), rectDxf(2250, 0, 1950, 1670),
    rectDxf(0, 2050, 1670, 235), rectDxf(1770, 2050, 1670, 235),
    rectDxf(0, 2420, 1950, 235), rectDxf(2050, 2420, 1950, 235),
  ].join("");
  write("02_raskroy_zerkal.dxf", dxfHeader() + mirror + dxfFooter);
  const cards = Array.from({ length: 6 }, (_, i) => rectDxf(i * 310, 0, 260, 390) + rectDxf(i * 310 + 18, 18, 224, 354, "ENGRAVE")).join("");
  write("03_mdf_karty_260x390.dxf", dxfHeader() + cards + dxfFooter);
  const chips = [
    ...Array.from({ length: 10 }, (_, i) => circleDxf(90 + (i % 5) * 185, 90 + Math.floor(i / 5) * 185, 72.5) + circleDxf(90 + (i % 5) * 185, 90 + Math.floor(i / 5) * 185, 43, "ENGRAVE")),
    ...Array.from({ length: 14 }, (_, i) => circleDxf(80 + (i % 7) * 130, 460 + Math.floor(i / 7) * 110, 42.5) + circleDxf(80 + (i % 7) * 130, 460 + Math.floor(i / 7) * 110, 24, "ENGRAVE")),
  ].join("");
  write("04_mdf_fishki_zhetony.dxf", dxfHeader() + chips + dxfFooter);
}

function tables() {
  const rows = [
    ["id", "type", "qty", "size_mm", "material", "note"],
    ["M01", "front semi mirror", 1, "2110 x 1830", "semi-transparent mirror", "final after frame measurement"],
    ["M02", "back mirror", 1, "1950 x 1670", "mirror", "behind objects"],
    ["M03-M04", "side mirrors", 2, "1670 x 235", "mirror", "left/right"],
    ["M05-M06", "top/bottom mirrors", 2, "1950 x 235", "mirror", "top/bottom"],
    ["K01-K06", "large cards", 6, "260 x 390", "MDF 6-8 mm painted", "fan"],
    ["C01-C08", "big chips", 8, "D145", "MDF 8-10 mm painted", "10 optional"],
    ["T01-T12", "tokens", 12, "D85", "MDF 6-8 mm painted", "14 optional"],
    ["S01-S36", "suits", "28-36", "45-75", "MDF 4-6 mm painted", "art contours in SVG"],
    ["LED", "LED strip", "23-28 m", "24V preferred", "warm/amber", "2-3 power zones"],
  ];
  write("vedomost_detalei.csv", rows.map((r) => r.join(";")).join("\n"));
  const coords = [
    ["id", "x_mm", "y_mm", "diameter_or_w_mm", "h_mm", "layer_depth_mm"],
    ["card_fan", 1065, 420, 900, 570, "90-125"],
    ...[[350,365,"C1"],[425,650,"C2"],[350,980,"C3"],[365,1350,"C4"],[1780,365,"C5"],[1705,650,"C6"],[1780,980,"C7"],[1765,1350,"C8"]].map(([x,y,id]) => [id,x,y,145,145,"55-85"]),
    ...[[360,515,"T1"],[420,810,"T2"],[370,1165,"T3"],[300,1510,"T4"],[1770,515,"T5"],[1710,810,"T6"],[1760,1165,"T7"],[1830,1510,"T8"],[620,1280,"T9"],[1510,1280,"T10"],[760,575,"T11"],[1370,575,"T12"]].map(([x,y,id]) => [id,x,y,85,85,"55-85"]),
  ];
  write("koordinaty_obektov.csv", coords.map((r) => r.join(";")).join("\n"));
  write("README.md", `# Чертежи casino mirror - чистая версия

Сделано заново по исходному референсу и техпроекту, без FreeCAD-модели.

Открывать сначала:
- 01_fasad_kompozicii.png / .pdf - главный лист, показывает композицию.
- 02_raskroy_zerkal.pdf / .dxf - зеркала.
- 03_mdf_karty_260x390.pdf / .dxf - карты.
- 04_mdf_fishki_zhetony_masti.pdf / .svg - фишки, жетоны, масти.
- 05_led_shema.pdf - схема света.
- vedomost_detalei.csv - ведомость деталей.
- koordinaty_obektov.csv - координаты объектов.

Это аккуратный эскизно-технический комплект. Перед производством нужно согласовать художественные контуры MDF-элементов и промерить готовый короб под зеркала.
`);
}

frontComposition();
mirrorSheet();
mdfSheets();
ledSheet();
dxfFiles();
tables();
console.log(`clean drawings generated: ${OUT}`);
