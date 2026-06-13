const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const memoryPath = path.join(root, 'AGENT_MEMORY.md');
const command = process.argv[2];
const text = process.argv.slice(3).join(' ').trim();

function usage() {
  console.log('Usage: npm run memory -- add "note"');
  console.log('       npm run memory -- search "query"');
  console.log('       npm run memory -- list');
}

function ensureMemoryFile() {
  if (!fs.existsSync(memoryPath)) {
    fs.writeFileSync(memoryPath, '# Agent Memory\n\n## Notes\n', 'utf8');
  }
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

ensureMemoryFile();

if (command === 'add') {
  if (!text) {
    usage();
    process.exit(1);
  }
  fs.appendFileSync(memoryPath, `\n- ${today()}: ${text}\n`, 'utf8');
  console.log(`[OK] Added memory note to ${path.relative(root, memoryPath)}`);
} else if (command === 'search') {
  if (!text) {
    usage();
    process.exit(1);
  }
  const query = text.toLowerCase();
  const lines = fs.readFileSync(memoryPath, 'utf8').split(/\r?\n/);
  const matches = lines.filter((line) => line.toLowerCase().includes(query));
  if (!matches.length) {
    console.log('[INFO] No matching memory notes found.');
  } else {
    for (const line of matches) {
      console.log(line);
    }
  }
} else if (command === 'list') {
  console.log(fs.readFileSync(memoryPath, 'utf8'));
} else {
  usage();
  process.exit(command ? 1 : 0);
}
