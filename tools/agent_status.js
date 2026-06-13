const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const required = [
  'AGENTS.md',
  'PROJECT_RULES.md',
  'AGENT_MEMORY.md',
  'DECISIONS.md',
  'EXPERIMENTS.md',
  'TASKS.md',
  'AGENT_ROLES.md',
  'PERMISSIONS.md',
  'evals/README.md',
  'evals/frontend_smoke.md',
  'evals/agent_operating_loop.md',
  'tools/agent_context.py',
  'tools/agent_log.py',
  'tools/agent_checkpoint.py',
  'tools/agent_evals.py',
  'tools/scene_status.py',
  'tools/scene_attempt.py',
];

let ok = true;
for (const relative of required) {
  const filePath = path.join(root, relative);
  const exists = fs.existsSync(filePath);
  console.log(`[${exists ? 'OK' : 'MISSING'}] ${relative}`);
  ok = ok && exists;
}

if (!ok) {
  process.exit(2);
}

console.log('[OK] Agent workspace scaffold is installed.');
