#!/bin/bash
# Deploy WP1 to production, or roll it back.
#
# Usage:
#   ./scripts/wp1/deploy.sh                  deploy the current origin/main
#   ./scripts/wp1/deploy.sh --rollback <tag> roll back to a previous image tag
#                                            (e.g. release-141 or sha-73ed612)
#
# A deploy pushes origin/main to the release branch, which triggers the
# publish workflow (.github/workflows/publish.yml) to build the three
# docker images. It then runs scripts/wp1/deploy-remote.sh on the production
# box, which waits for the images tagged with the pushed commit's sha to
# appear on ghcr.io, pulls them, restarts the containers and applies
# database migrations.
#
# Requirements: push access to the GitHub repo, and ssh access (with
# sudo) to the production box on Wikimedia Cloud VPS (override the host
# with WP1_DEPLOY_HOST). See "Updating production" in the README for
# the one-time Wikimedia developer account / bastion SSH setup.
set -euo pipefail

REMOTE_HOST=${WP1_DEPLOY_HOST:-mwcurator-b.mwoffliner.eqiad1.wikimedia.cloud}
REMOTE_DIR=/data/code/wp1

usage() {
  sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
  exit 64
}

if [[ "${1:-}" == "--rollback" ]]; then
  tag=${2:-}
  [[ -n "$tag" ]] || usage
  exec ssh -t "$REMOTE_HOST" \
    "cd $REMOTE_DIR && sudo ./scripts/wp1/deploy-remote.sh --rollback '$tag'"
fi

[[ $# -eq 0 ]] || usage

git fetch origin
sha=$(git rev-parse origin/main)

# Plain, non-forced push: if release has somehow diverged from main this
# is rejected, and a human should sort it out locally. Never force this.
echo "==> Pushing origin/main ($sha) to release"
git push origin "$sha:refs/heads/release"

# Pull on the box first, so the deploy-remote.sh that runs is the one
# from the commit being deployed, not a stale copy.
echo "==> Running remote deploy on $REMOTE_HOST"
exec ssh -t "$REMOTE_HOST" \
  "cd $REMOTE_DIR && sudo git pull --ff-only origin main && sudo ./scripts/wp1/deploy-remote.sh '$sha'"
