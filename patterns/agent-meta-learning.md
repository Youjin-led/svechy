# Agent Meta-Learning

Use to improve strategy choice over time without unsafe recursive self-editing.

## Loop

1. Choose a strategy:
   `npm run agent:meta -- choose --task "..." --domain frontend`
2. Complete the task.
3. Log the task and meta episode:
   `npm run agent:log -- --title "..." --summary "..." --meta-strategy visual_reference --meta-reward 0.8`
4. Inspect accumulated results:
   `npm run agent:meta -- stats`
5. Derive a candidate strategy only when enough data exists:
   `npm run agent:meta -- improve --min-episodes 3`

## Safety

- Strategy candidates do not rewrite code or prompts automatically.
- Use explicit user intent before enabling recursive self-improvement.
