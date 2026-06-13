# Meta-Learning Eval

## Goal

Check that the agent can record learning episodes, choose strategies from past results, and derive improved strategy candidates without changing its own code automatically.

## Criteria

- `agent:meta init` creates the meta-learning SQLite tables and default strategies.
- `agent:meta choose` returns a JSON strategy for a task/domain/complexity.
- `agent:meta record` stores a completed `MetaEpisode` with reward, cost, duration, domain, complexity, and novelty.
- `agent:meta stats` summarizes accumulated episodes.
- `agent:meta improve` only creates a candidate strategy from enough data; it does not auto-edit prompts, tools, or project code.
- `agent:log --meta-strategy ...` can record an ordinary task log and a meta episode in one command.

## Commands

- `npm run agent:meta -- init`
- `npm run agent:meta -- choose --task "..." --domain frontend`
- `npm run agent:meta -- record --task "..." --strategy default --reward 0.8`
- `npm run agent:meta -- stats`
- `npm run agent:meta -- improve --min-episodes 3`
- `npm run agent:log -- --title "..." --summary "..." --meta-strategy default --meta-reward 0.8`
