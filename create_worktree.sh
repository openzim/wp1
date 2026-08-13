#!/usr/bin/env bash
# Create a git worktree for WP1 with the untracked credentials files copied
# in. A bare `git worktree add` leaves out wp1/credentials.py.dev (it's
# untracked), and docker-compose-dev.yml bind-mounts that file — when it's
# missing, Docker creates a root-owned directory at its path and the dev
# stack fails to start.
#
# Usage: ./create_worktree.sh <branch> [start-point]
#   <branch>       branch to check out in the worktree; created from
#                  [start-point] if it doesn't exist yet
#   [start-point]  ref a new branch is created from (default: main)
#
# The worktree is created at .worktrees/<branch>.
set -euo pipefail

cd "$(dirname "$0")"

branch="${1:?usage: $0 <branch> [start-point]}"
start="${2:-main}"
dest=".worktrees/$branch"

if [ -e "$dest" ]; then
  echo "error: $dest already exists" >&2
  exit 1
fi

if git show-ref --verify --quiet "refs/heads/$branch"; then
  git worktree add "$dest" "$branch"
else
  git worktree add -b "$branch" "$dest" "$start"
fi

# Copy every credentials variant present here but absent from the fresh
# checkout (i.e. the untracked ones; tracked variants already exist there).
copied=0
for f in wp1/credentials.py*; do
  [ -f "$f" ] || continue
  if [ ! -e "$dest/$f" ]; then
    cp -p "$f" "$dest/$f"
    echo "copied $f -> $dest/$f"
    copied=$((copied + 1))
  fi
done

echo "worktree ready at $dest ($copied credentials file(s) copied)"
