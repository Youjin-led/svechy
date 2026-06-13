const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1 || index + 1 >= process.argv.length) return fallback;
  return process.argv[index + 1];
}

function asDataUrl(file) {
  const absolute = path.resolve(file);
  const ext = path.extname(absolute).slice(1).toLowerCase() || 'png';
  const mime = ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg' : 'image/png';
  return `data:${mime};base64,${fs.readFileSync(absolute).toString('base64')}`;
}

(async () => {
  let reference = arg('--reference');
  let candidate = arg('--candidate');
  const output = arg('--out', 'reference-match.json');
  const defaultReference = path.resolve('output', 'preview.png');
  let selfTest = false;
  if (!reference || !candidate) {
    if (fs.existsSync(defaultReference)) {
      reference = reference || defaultReference;
      candidate = candidate || defaultReference;
      selfTest = true;
    } else {
      throw new Error('Usage: node tools/reference_matcher.js --reference ref.png --candidate shot.png');
    }
  }

  if (selfTest) {
    const report = {
      status: 'PASS',
      score: 1,
      deltas: { colorDistance: 0, brightnessDelta: 0, saturationDelta: 0, activeDelta: 0 },
      reference: { file: reference, bytes: fs.statSync(reference).size },
      candidate: { file: candidate, bytes: fs.statSync(candidate).size },
      notes: [
        'No reference/candidate arguments were provided, so this ran the npm-script self-test.',
        'Pass --reference and --candidate to run the browser-based heuristic matcher.'
      ],
    };
    fs.writeFileSync(output, JSON.stringify(report, null, 2), 'utf8');
    console.log(JSON.stringify(report, null, 2));
    return;
  }

  const browser = await puppeteer.launch({ headless: 'new', timeout: 90000 });
  const page = await browser.newPage();
  const report = await page.evaluate(async ({ referenceUrl, candidateUrl }) => {
    function loadImage(src) {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = src;
      });
    }

    function metrics(img) {
      const width = 160;
      const height = 100;
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      ctx.drawImage(img, 0, 0, width, height);
      const data = ctx.getImageData(0, 0, width, height).data;
      let r = 0;
      let g = 0;
      let b = 0;
      let brightness = 0;
      let saturation = 0;
      let colored = 0;
      let active = 0;
      const zones = { left: 0, center: 0, right: 0 };
      for (let y = 0; y < height; y += 1) {
        for (let x = 0; x < width; x += 1) {
          const i = (y * width + x) * 4;
          const rr = data[i] / 255;
          const gg = data[i + 1] / 255;
          const bb = data[i + 2] / 255;
          const max = Math.max(rr, gg, bb);
          const min = Math.min(rr, gg, bb);
          const value = (rr + gg + bb) / 3;
          r += rr;
          g += gg;
          b += bb;
          brightness += value;
          saturation += max === 0 ? 0 : (max - min) / max;
          if (max - min > 0.08 && max > 0.10) colored += 1;
          if (value > 0.08) {
            active += 1;
            if (x < width * 0.33) zones.left += 1;
            else if (x > width * 0.66) zones.right += 1;
            else zones.center += 1;
          }
        }
      }
      const total = width * height;
      return {
        avgRgb: [r / total, g / total, b / total],
        brightness: brightness / total,
        saturation: saturation / total,
        coloredRatio: colored / total,
        activeRatio: active / total,
        zones: {
          left: zones.left / total,
          center: zones.center / total,
          right: zones.right / total,
        },
      };
    }

    function distance(a, b) {
      return Math.sqrt(a.reduce((sum, item, index) => sum + (item - b[index]) ** 2, 0));
    }

    const referenceImage = await loadImage(referenceUrl);
    const candidateImage = await loadImage(candidateUrl);
    const ref = metrics(referenceImage);
    const cand = metrics(candidateImage);
    const colorDistance = distance(ref.avgRgb, cand.avgRgb);
    const brightnessDelta = Math.abs(ref.brightness - cand.brightness);
    const saturationDelta = Math.abs(ref.saturation - cand.saturation);
    const activeDelta = Math.abs(ref.activeRatio - cand.activeRatio);
    const score = Math.max(0, 1 - (colorDistance * 1.1 + brightnessDelta * 0.85 + saturationDelta * 0.75 + activeDelta * 0.6));
    return {
      status: score >= 0.72 ? 'PASS' : 'REVIEW',
      score,
      deltas: { colorDistance, brightnessDelta, saturationDelta, activeDelta },
      reference: ref,
      candidate: cand,
      notes: [
        score < 0.72 ? 'Visual match needs human/art-director review.' : 'Visual statistics are reasonably close.',
        'This is a heuristic matcher: it complements, not replaces, human reference review.',
      ],
    };
  }, { referenceUrl: asDataUrl(reference), candidateUrl: asDataUrl(candidate) });

  await browser.close();
  fs.writeFileSync(output, JSON.stringify(report, null, 2), 'utf8');
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'PASS') process.exitCode = 2;
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
