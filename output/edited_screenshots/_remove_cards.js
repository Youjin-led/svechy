const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

const root = path.resolve(__dirname, '..', '..');
const outDir = path.join(root, 'output', 'edited_screenshots');
const shots = [
  {
    input: 'C:/Users/Ардор/OneDrive/Изображения/Screenshots/Снимок экрана 2026-05-14 133450.png',
    output: 'screenshot-133450-cards-removed.png',
    spineX: 915,
    polygons: [
      [[420,226],[1244,250],[1255,798],[420,754]],
      [[1328,454],[1631,486],[1640,842],[1326,813]],
      [[605,773],[1168,806],[1168,912],[604,912]],
      [[470,874],[564,874],[566,912],[471,912]]
    ]
  },
  {
    input: 'C:/Users/Ардор/OneDrive/Изображения/Screenshots/Снимок экрана 2026-05-14 133501.png',
    output: 'screenshot-133501-cards-removed.png',
    spineX: 820,
    polygons: [
      [[169,75],[895,37],[897,644],[169,574]],
      [[1054,263],[1667,334],[1663,814],[1052,744]],
      [[166,0],[314,0],[315,75],[166,76]],
      [[1583,0],[1839,0],[1839,78],[1582,79]],
      [[1713,542],[1839,518],[1839,831],[1712,837]]
    ]
  },
  {
    input: 'C:/Users/Ардор/OneDrive/Изображения/Screenshots/Снимок экрана 2026-05-14 133518.png',
    output: 'screenshot-133518-cards-removed.png',
    spineX: 835,
    polygons: [
      [[148,58],[671,10],[673,628],[148,539]],
      [[857,250],[1628,303],[1653,832],[858,833]],
      [[775,0],[1130,0],[1130,257],[774,258]],
      [[1350,0],[1570,0],[1570,80],[1350,80]]
    ]
  },
  {
    input: 'C:/Users/Ардор/OneDrive/Изображения/Screenshots/Снимок экрана 2026-05-14 133527.png',
    output: 'screenshot-133527-cards-removed.png',
    spineX: 900,
    polygons: [
      [[539,202],[1327,221],[1328,743],[539,676]],
      [[1400,450],[1665,483],[1665,869],[1400,895]],
      [[258,41],[441,102],[441,519],[258,480]],
      [[884,672],[1358,653],[1358,912],[884,912]],
      [[1334,0],[1556,0],[1555,78],[1334,78]]
    ]
  },
  {
    input: 'C:/Users/Ардор/OneDrive/Изображения/Screenshots/Снимок экрана 2026-05-14 133541.png',
    output: 'screenshot-133541-cards-removed.png',
    spineX: 880,
    polygons: [
      [[236,105],[846,51],[846,657],[236,577]],
      [[1012,283],[1711,336],[1711,870],[1012,870]],
      [[330,13],[676,0],[676,95],[330,105]],
      [[160,0],[236,0],[236,421],[160,421]]
    ]
  }
];

(async () => {
  const browser = await puppeteer.launch({ headless: 'new', protocolTimeout: 600000 });
  const page = await browser.newPage();
  page.setDefaultTimeout(0);
  await page.setViewport({ width: 1900, height: 950, deviceScaleFactor: 1 });

  for (const shot of shots) {
    const src = fs.readFileSync(shot.input).toString('base64');
    const result = await page.evaluate(async ({ src, polygons, spineX }) => {
      const img = new Image();
      img.src = `data:image/png;base64,${src}`;
      await img.decode();

      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      ctx.drawImage(img, 0, 0);

      const maskCanvas = document.createElement('canvas');
      maskCanvas.width = img.width;
      maskCanvas.height = img.height;
      const maskCtx = maskCanvas.getContext('2d', { willReadFrequently: true });
      maskCtx.fillStyle = '#000';
      maskCtx.fillRect(0, 0, img.width, img.height);
      maskCtx.fillStyle = '#fff';
      for (const poly of polygons) {
        maskCtx.beginPath();
        maskCtx.moveTo(poly[0][0], poly[0][1]);
        for (let i = 1; i < poly.length; i++) maskCtx.lineTo(poly[i][0], poly[i][1]);
        maskCtx.closePath();
        maskCtx.fill();
      }
      const feather = 12;
      maskCtx.filter = `blur(${feather}px)`;
      maskCtx.globalCompositeOperation = 'source-over';
      for (const poly of polygons) {
        maskCtx.beginPath();
        maskCtx.moveTo(poly[0][0], poly[0][1]);
        for (let i = 1; i < poly.length; i++) maskCtx.lineTo(poly[i][0], poly[i][1]);
        maskCtx.closePath();
        maskCtx.fill();
      }
      maskCtx.filter = 'none';

      const w = img.width;
      const h = img.height;

      const fill = document.createElement('canvas');
      fill.width = w;
      fill.height = h;
      const fctx = fill.getContext('2d');
      fctx.fillStyle = '#02090b';
      fctx.fillRect(0, 0, w, h);
      fctx.filter = 'blur(74px) brightness(0.48) saturate(1.35)';
      fctx.drawImage(img, -80, -80, w + 160, h + 160);
      fctx.filter = 'none';
      fctx.globalCompositeOperation = 'screen';
      const haze = fctx.createRadialGradient(spineX, h * 0.5, 20, spineX, h * 0.5, 620);
      haze.addColorStop(0, 'rgba(18,105,125,0.30)');
      haze.addColorStop(0.45, 'rgba(55,22,95,0.18)');
      haze.addColorStop(1, 'rgba(0,0,0,0)');
      fctx.fillStyle = haze;
      fctx.fillRect(0, 0, w, h);

      ctx.save();
      ctx.beginPath();
      for (const poly of polygons) {
        ctx.moveTo(poly[0][0], poly[0][1]);
        for (let i = 1; i < poly.length; i++) ctx.lineTo(poly[i][0], poly[i][1]);
        ctx.closePath();
      }
      ctx.clip();
      ctx.drawImage(fill, 0, 0);

      function drawVertebra(cx, cy, scale, rot, alpha) {
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(rot);
        ctx.scale(scale, scale);
        ctx.globalAlpha = alpha;
        const body = ctx.createRadialGradient(0, 0, 6, 0, 0, 70);
        body.addColorStop(0, 'rgba(185,225,245,0.22)');
        body.addColorStop(0.24, 'rgba(74,40,112,0.62)');
        body.addColorStop(0.62, 'rgba(12,20,38,0.88)');
        body.addColorStop(1, 'rgba(1,5,10,0.05)');
        ctx.fillStyle = body;
        ctx.beginPath();
        ctx.ellipse(0, 0, 72, 29, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = 'rgba(10,13,24,0.78)';
        ctx.beginPath();
        ctx.ellipse(0, 0, 30, 12, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = 'rgba(62,218,240,0.36)';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.ellipse(-5, -2, 76, 31, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.strokeStyle = 'rgba(226,72,222,0.28)';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(-80, 6);
        ctx.bezierCurveTo(-42, -30, 42, 31, 86, -4);
        ctx.stroke();
        ctx.restore();
      }

      ctx.globalCompositeOperation = 'source-over';
      for (let y = -40; y < h + 70; y += 54) {
        const cx = spineX + Math.sin(y * 0.018) * 34 + (Math.random() - 0.5) * 18;
        drawVertebra(cx, y, 0.82 + Math.random() * 0.22, Math.sin(y * 0.011) * 0.22, 0.78);
      }

      ctx.globalCompositeOperation = 'screen';
      const colors = ['rgba(35,215,255,0.55)', 'rgba(232,67,214,0.45)', 'rgba(44,255,140,0.42)', 'rgba(112,78,255,0.40)'];
      for (let i = 0; i < 720; i++) {
        const x = spineX + (Math.random() - 0.5) * 650;
        const y = Math.random() * h;
        const r = 1 + Math.random() * 4.5;
        ctx.fillStyle = colors[(Math.random() * colors.length) | 0];
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalCompositeOperation = 'multiply';
      ctx.fillStyle = 'rgba(0,8,10,0.28)';
      ctx.fillRect(0, 0, w, h);
      ctx.restore();

      ctx.globalCompositeOperation = 'source-over';
      const grain = ctx.createImageData(w, h);
      for (let i = 0; i < grain.data.length; i += 4) {
        const v = 95 + Math.random() * 80;
        grain.data[i] = v;
        grain.data[i + 1] = v;
        grain.data[i + 2] = v;
        grain.data[i + 3] = 10;
      }
      const grainCanvas = document.createElement('canvas');
      grainCanvas.width = w;
      grainCanvas.height = h;
      grainCanvas.getContext('2d').putImageData(grain, 0, 0);
      ctx.drawImage(grainCanvas, 0, 0);
      return canvas.toDataURL('image/png').split(',')[1];
    }, { src, polygons: shot.polygons, spineX: shot.spineX });

    const outPath = path.join(outDir, shot.output);
    fs.writeFileSync(outPath, Buffer.from(result, 'base64'));
    console.log(outPath);
  }

  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
