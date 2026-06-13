# Max Agent Upgrade Eval

## Goal

Check that the agent has local infrastructure for long-running work, reusable patterns, visual reference matching, and meta-learning without unsafe autonomous code rewriting.

## Criteria

- `agent:goal` can create/list/show a goal queue.
- `visual:match` can compare a candidate screenshot to a reference image and return a JSON report.
- `patterns/` contains reusable recipes for 3D/frontend and agent workflows.
- `agent:evals` checks the new tools and docs.
- The system remains human-in-the-loop for dangerous operations and recursive self-improvement.

## Commands

- `npm run agent:goal -- create "..." --domain frontend --strategy visual_reference`
- `npm run agent:goal -- list`
- `npm run visual:match -- --reference ref.png --candidate shot.png`
- `npm run agent:evals`
