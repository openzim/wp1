#!/bin/bash
# Runs ON the production box (mwcurator), as root, invoked by
# scripts/wp1/deploy.sh. Can also be run by hand from /data/code/wp1.
#
# Usage:
#   deploy-remote.sh <full-git-sha>       deploy the images built from that sha
#   deploy-remote.sh --rollback <tag>     re-tag <tag> as release and restart
#                                         (tag: release-<N> or sha-<XXXXXXX>)
set -euo pipefail

cd "$(dirname "$0")/.."

REGISTRY=ghcr.io/openzim
IMAGES=(wp1-workers wp1-web wp1-frontend)
CONTAINERS=(wp1bot-workers wp1bot-web wp1bot-frontend)
LAST_DEPLOY_FILE=.last-deploy
POLL_INTERVAL=30
POLL_TIMEOUT=$((45 * 60))

if [[ $EUID -ne 0 ]]; then
  echo "error: must be run as root (docker access)" >&2
  exit 1
fi

# Pull the given tag for the three wp1 images, re-tag it locally as
# `release` (the tag docker-compose.yml uses), and recreate containers.
#
# Only ever pull these three images explicitly -- never `docker compose
# pull`, which would also refresh infrastructure images like redis. A
# surprise redis recreation from an unpinned image destroyed the queue
# and log history once already (issue #1244).
retag_and_up() {
  local tag=$1 img
  for img in "${IMAGES[@]}"; do
    docker pull "$REGISTRY/$img:$tag"
    docker tag "$REGISTRY/$img:$tag" "$REGISTRY/$img:release"
  done
  echo "==> Recreating containers"
  docker compose up -d
}

verify() {
  local c status ok=1
  echo "==> Verifying containers"
  sleep 10
  for c in "${CONTAINERS[@]}"; do
    status=$(docker inspect -f '{{.State.Status}}' "$c" 2>/dev/null || echo missing)
    echo "    $c: $status"
    [[ "$status" == "running" ]] || ok=0
  done
  echo "==> Verifying API (https://api.wp1.openzim.org)"
  if curl -fsS --max-time 30 https://api.wp1.openzim.org/v1/projects/count \
      | grep -q '"count"'; then
    echo "    API OK"
  else
    echo "    API check FAILED"
    ok=0
  fi
  echo "==> Verifying frontend (https://wp1.openzim.org)"
  if curl -fsS --max-time 30 https://wp1.openzim.org/ | grep -qi '<html'; then
    echo "    frontend OK"
  else
    echo "    frontend check FAILED"
    ok=0
  fi
  [[ $ok -eq 1 ]]
}

if [[ "${1:-}" == "--rollback" ]]; then
  tag=${2:?usage: deploy-remote.sh --rollback <release-N|sha-XXXXXXX>}
  echo "==> Rolling back to $tag"
  retag_and_up "$tag"
  verify
  # Deliberately does not touch $LAST_DEPLOY_FILE: the next deploy's
  # env-schema diff then spans the rolled-back range too, which is the
  # safe direction.
  cat <<'EOF'
==> Rollback complete.
    If the deploy being rolled back included database migrations, roll
    them back by hand after checking what they were:
      docker exec -e PYTHONPATH=. wp1bot-workers \
        yoyo -c /usr/src/app/db/production/yoyo.ini rollback
    The next normal deploy rolls the images forward again.
EOF
  exit 0
fi

sha=${1:?usage: deploy-remote.sh <full-git-sha>}
short=$(git rev-parse --short=7 "$sha")
prev=$(cat "$LAST_DEPLOY_FILE" 2>/dev/null || true)

# The production env file on this box (/data/wp1bot/wp1.env, consumed by
# docker-compose.yml via env_file) is managed by hand. If the generated
# .env.example changed since the last deploy, the real file probably
# needs a matching edit -- stop and ask.
if [[ -n "$prev" ]] && git cat-file -e "$prev" 2>/dev/null; then
  if [[ -n "$(git diff --name-only "$prev".."$sha" -- .env.example 2>/dev/null)" ]]; then
    cat <<EOF

*** WARNING: the env schema (.env.example) changed since the last deploy
*** ($prev). Make sure /data/wp1bot/wp1.env has been
*** updated to match before continuing.

EOF
    read -r -p "Continue with deploy? [y/N] " answer </dev/tty
    [[ "$answer" == [yY]* ]] || { echo "Aborted."; exit 1; }
  fi
else
  echo "note: no previous deploy recorded; skipping env-schema-change check"
fi

# Wait for the publish workflow to push all three images for this exact
# commit. Polling the immutable sha tag (rather than pulling the moving
# `release` tag) guarantees a consistent image set: the three matrix
# jobs finish at different times, and `release` can briefly point at a
# mixed set while the workflow is mid-flight.
echo "==> Waiting for images tagged sha-$short on $REGISTRY (timeout ${POLL_TIMEOUT}s)"
deadline=$((SECONDS + POLL_TIMEOUT))
for img in "${IMAGES[@]}"; do
  until docker manifest inspect "$REGISTRY/$img:sha-$short" >/dev/null 2>&1; do
    if ((SECONDS >= deadline)); then
      echo "error: timed out waiting for $REGISTRY/$img:sha-$short" >&2
      echo "check https://github.com/openzim/wp1/actions/workflows/publish.yml" >&2
      exit 1
    fi
    sleep "$POLL_INTERVAL"
  done
  echo "    $img:sha-$short available"
done

retag_and_up "sha-$short"

echo "==> Applying database migrations"
docker exec -e PYTHONPATH=. wp1bot-workers \
  yoyo -c /usr/src/app/db/production/yoyo.ini apply --batch

verify

echo "$sha" > "$LAST_DEPLOY_FILE"
echo "==> Deployed $sha"
if [[ -n "$prev" ]]; then
  echo "    Roll back with: ./scripts/wp1/deploy.sh --rollback sha-$(git rev-parse --short=7 "$prev" 2>/dev/null || echo "$prev")"
fi
