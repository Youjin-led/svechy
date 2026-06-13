const fs = require('fs');
const path = require('path');
const puppeteer = require('../node_modules/puppeteer');

function fileUrl(filePath) {
  return `file:///${path.resolve(filePath).replace(/\\/g, '/')}`;
}

async function main() {
  const videoPath = process.argv[2];
  const outDir = process.argv[3] || path.join('output', 'reference_frames');
  if (!videoPath) {
    console.error('Usage: node tools/extract_video_frames.js <video.mp4> [outDir]');
    process.exit(2);
  }
  fs.mkdirSync(outDir, { recursive: true });

  console.error('Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    timeout: 120000,
    args: ['--allow-file-access-from-files', '--autoplay-policy=no-user-gesture-required'],
  });
  const page = await browser.newPage();
  page.setDefaultTimeout(120000);
  page.setDefaultNavigationTimeout(120000);
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  console.error('Preparing page...');
  await page.setContent(`
    <!doctype html>
    <video id="video" crossorigin="anonymous" preload="auto" muted playsinline></video>
    <canvas id="canvas"></canvas>
  `);

  const src = fileUrl(videoPath);
  console.error(`Loading video: ${src}`);
  await page.evaluate((videoSrc) => {
    const video = document.getElementById('video');
    video.src = videoSrc;
    video.load();
  }, src);

  console.error('Waiting metadata...');
  const metadata = await page.evaluate(async () => {
    const video = document.getElementById('video');
    await new Promise((resolve, reject) => {
      video.onloadedmetadata = resolve;
      video.onerror = () => {
        const err = video.error;
        reject(new Error(`Failed to load video metadata: ${err ? `${err.code} ${err.message}` : 'unknown error'}`));
      };
    });
    return { duration: video.duration, width: video.videoWidth, height: video.videoHeight };
  });

  const times = [
    metadata.duration * 0.08,
    metadata.duration * 0.22,
    metadata.duration * 0.38,
    metadata.duration * 0.55,
    metadata.duration * 0.72,
    metadata.duration * 0.88,
  ].map((time) => Math.min(Math.max(time, 0), metadata.duration - 0.05));

  const frames = [];
  for (let i = 0; i < times.length; i += 1) {
    const payload = await page.evaluate(async (time) => {
      const video = document.getElementById('video');
      const canvas = document.getElementById('canvas');
      video.currentTime = time;
      await new Promise((resolve, reject) => {
        video.onseeked = resolve;
        video.onerror = () => reject(new Error('Video seek failed'));
      });
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      return canvas.toDataURL('image/png').split(',')[1];
    }, times[i]);
    const filename = path.join(outDir, `frame_${String(i + 1).padStart(2, '0')}.png`);
    fs.writeFileSync(filename, Buffer.from(payload, 'base64'));
    frames.push({ time: times[i], filename });
  }

  await browser.close();
  console.log(JSON.stringify({ metadata, frames }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message);
  process.exit(1);
});
