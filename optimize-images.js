/**
 * Скрипт оптимизации изображений для сайта Svetlo
 * Конвертирует PNG → WebP, сжимает JPG, уменьшает размер
 * Запуск: node optimize-images.js
 */

const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const ASSETS_DIR = path.join(__dirname, 'assets');
const QUALITY_WEBP = 75; // качество WebP (0-100)
const QUALITY_JPEG = 75;
const MAX_WIDTH = 1200; // максимальная ширина для контентных изображений

async function optimizeFile(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const basename = path.basename(filePath);
  const dir = path.dirname(filePath);
  const nameWithoutExt = path.basename(filePath, ext);

  // Пропускаем уже оптимизированные
  if (basename.endsWith('.webp') || basename.endsWith('.avif')) return;

  try {
    const image = sharp(filePath);
    const metadata = await image.metadata();

    // Если ширина больше MAX_WIDTH — ресайзим
    let pipeline = image;
    if (metadata.width > MAX_WIDTH) {
      pipeline = pipeline.resize(MAX_WIDTH, null, { fit: 'inside', withoutEnlargement: true });
    }

    if (ext === '.png') {
      // Конвертируем PNG → WebP
      const webpPath = path.join(dir, `${nameWithoutExt}.webp`);
      await pipeline
        .webp({ quality: QUALITY_WEBP, effort: 4 })
        .toFile(webpPath);

      const oldSize = fs.statSync(filePath).size;
      const newSize = fs.statSync(webpPath).size;
      const saved = ((oldSize - newSize) / oldSize * 100).toFixed(1);
      console.log(`✅ ${basename} → ${nameWithoutExt}.webp (${(oldSize / 1024).toFixed(0)}KB → ${(newSize / 1024).toFixed(0)}KB, -${saved}%)`);

      // Оставляем оригинал PNG, но можно удалить если нужно
      // fs.unlinkSync(filePath);
    } else if (ext === '.jpg' || ext === '.jpeg') {
      // Конвертируем JPEG → WebP
      const webpPath = path.join(dir, `${nameWithoutExt}.webp`);
      await pipeline
        .webp({ quality: QUALITY_WEBP, effort: 4 })
        .toFile(webpPath);

      const oldSize = fs.statSync(filePath).size;
      const newSize = fs.statSync(webpPath).size;
      const saved = ((oldSize - newSize) / oldSize * 100).toFixed(1);
      console.log(`✅ ${basename} → ${nameWithoutExt}.webp (${(oldSize / 1024).toFixed(0)}KB → ${(newSize / 1024).toFixed(0)}KB, -${saved}%)`);
    }
  } catch (err) {
    console.error(`❌ Ошибка обработки ${basename}: ${err.message}`);
  }
}

async function walkDir(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      await walkDir(fullPath);
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name).toLowerCase();
      if (['.png', '.jpg', '.jpeg'].includes(ext)) {
        await optimizeFile(fullPath);
      }
    }
  }
}

async function main() {
  console.log('🚀 Начинаю оптимизацию изображений...\n');
  const start = Date.now();
  await walkDir(ASSETS_DIR);
  const elapsed = ((Date.now() - start) / 1000).toFixed(1);
  console.log(`\n✨ Готово за ${elapsed}с!`);
}

main().catch(console.error);
