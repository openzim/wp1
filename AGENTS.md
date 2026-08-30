# AGENTS.md

## Worktrees

Major work — implementing specs, fixing bugs — happens in a worktree, not the main checkout. Create it with `scripts/util/create_worktree.sh <branch>` (lands at `.worktrees/<branch>`). Use the script, not bare `git worktree add`: it copies the untracked credentials files and writes a port-offset `.env` so the worktree's dev stack runs alongside the main one.

## Agent artifacts

Generated specs, implementation plans, and working notes go in `./agents/`. `./docs/` belongs to the repo itself — NEVER write agent artifacts there.
