#!/usr/bin/env bash

# Call it once to create a `test-worker` for local development:
# - retrieve an admin token
# - generate an SSH key pair for the worker
# - create the `test-worker` worker, registering its public key
# - grant it the `wikimedia` context
#
# The context grant is required: WP1 creates all of its recipes with the
# `wikimedia` context, and the Zimfarm scheduler only offers those tasks to
# workers holding that context — a worker without it stays idle forever while
# tasks sit in "requested".
#
# The worker-manager container (compose profile `zimfarm-worker`)
# authenticates with the generated private key and performs its own check-in,
# reporting its resources and supported offliners. The current Zimfarm API has
# no users endpoint, so no user account and no manual check-in are involved.
#
# Safe to re-run: if the worker already exists, the freshly generated public
# key is added to it and the context grant is re-applied.

set -e

ZIMFARM_BASE_API_URL="http://localhost:8004/v2"
# Must match the `--name` passed to worker-manager in docker-compose-dev.yml.
# The API requires ^[a-z0-9-]+$ (no underscores).
WORKER_NAME="test-worker"

die() {
    echo "ERROR: $1" >&2
    exit 1
}

error_from() {
    echo "$1" | jq -r '.errors // .message // .detail // "Unknown error"' 2>/dev/null || echo "$2"
}

echo "Retrieving admin access token"

ZF_ADMIN_TOKEN="$(curl -s -X 'POST' \
    "${ZIMFARM_BASE_API_URL}/auth/authorize" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"username": "admin", "password": "admin"}' \
    | jq -r '.access_token')"

if [ -z "$ZF_ADMIN_TOKEN" ] || [ "$ZF_ADMIN_TOKEN" = "null" ]; then
    die "Failed to retrieve admin access token"
fi

echo "Generating SSH key pair (Ed25519)"
rm -f id_ed25519 id_ed25519.pub
ssh-keygen -t ed25519 -f id_ed25519 -N ""

# The API returns a 500 (not 409) when creating a worker that already exists,
# so check for existence up front instead of interpreting the create response.
exists_code=$(curl -s -o /dev/null -w "%{http_code}" \
    "${ZIMFARM_BASE_API_URL}/workers/${WORKER_NAME}" \
    -H "Authorization: Bearer ${ZF_ADMIN_TOKEN}")

if [ "$exists_code" -eq 404 ]; then
    echo "Creating worker '${WORKER_NAME}' with its public key"
    payload="$(jq -n --arg name "$WORKER_NAME" --arg key "$(< id_ed25519.pub)" \
        '{name: $name, ssh_key: {key: $key}}')"
    response=$(curl -s -w "\n%{http_code}" -X POST "${ZIMFARM_BASE_API_URL}/workers" \
        -H 'accept: application/json' \
        -H "Authorization: Bearer ${ZF_ADMIN_TOKEN}" \
        -H 'Content-Type: application/json' \
        -d "$payload")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    if [ "$http_code" -lt 200 ] || [ "$http_code" -ge 300 ]; then
        die "Could not create worker: $(error_from "$body" "HTTP $http_code")"
    fi
elif [ "$exists_code" -ge 200 ] && [ "$exists_code" -lt 300 ]; then
    echo "Worker already exists; registering the new public key with it"
    key_payload="$(jq -n --arg key "$(< id_ed25519.pub)" '{key: $key}')"
    response=$(curl -s -w "\n%{http_code}" -X POST \
        "${ZIMFARM_BASE_API_URL}/workers/${WORKER_NAME}/keys" \
        -H 'accept: application/json' \
        -H "Authorization: Bearer ${ZF_ADMIN_TOKEN}" \
        -H 'Content-Type: application/json' \
        -d "$key_payload")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    if [ "$http_code" -lt 200 ] || [ "$http_code" -ge 300 ]; then
        die "Could not register new key: $(error_from "$body" "HTTP $http_code")"
    fi
else
    die "Could not check worker existence: HTTP $exists_code"
fi

echo "Granting the 'wikimedia' context to '${WORKER_NAME}'"
response=$(curl -s -w "\n%{http_code}" -X PUT \
    "${ZIMFARM_BASE_API_URL}/workers/${WORKER_NAME}" \
    -H 'accept: application/json' \
    -H "Authorization: Bearer ${ZF_ADMIN_TOKEN}" \
    -H 'Content-Type: application/json' \
    -d '{"contexts": {"wikimedia": null}}')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n -1)
if [ "$http_code" -lt 200 ] || [ "$http_code" -ge 300 ]; then
    die "Could not grant context: $(error_from "$body" "HTTP $http_code")"
fi

echo "DONE"
