#!/usr/bin/env bash

# Script to register offliners in Zimfarm
# - retrieve an admin token
# - fetch offliner definitions from their respective GitHub repositories OR Zimfarm API
# - register each offliner and its definition with the backend API

set -e

# List of offliners to register
OFFLINERS=("mwoffliner")

ZIMFARM_BASE_API_URL="http://localhost:8004/v2"
OFFLINER_DEFINITIONS_BASE_URL="https://api.farm.openzim.org/v2"

# Offliner configuration data for API registration
declare -A offliner_configs

# Declare associative arrays to store offliner definitions and versions
declare -A offliner_definitions
declare -A offliner_versions

# Initialize offliner configurations
setup_offliner_configs() {
    offliner_configs["mwoffliner"]='{"base_model":"DashModel","docker_image_name":"openzim/mwoffliner","command_name":"mwoffliner"}'
}

die() {
    echo "ERROR: $1" >&2
    exit 1
}

# Fetch available versions for an offliner from Zimfarm API
fetch_offliner_versions() {
    local offliner_name="$1"
    local url="${OFFLINER_DEFINITIONS_BASE_URL}/offliners/${offliner_name}/versions"

    local response
    local http_code
    response=$(curl -s -w "\n%{http_code}" "$url")

    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | head -n1)

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        :
    else
        error_msg=$(echo "$response" | jq -r '.errors // .message // .detail // "Unknown error"' 2>/dev/null || echo "HTTP $http_code")
        die "Failed to fetch versions for ${offliner_name} from ${url}: ${error_msg}"
    fi

    if ! echo "$response" | jq . >/dev/null 2>&1; then
        die "Invalid JSON received for ${offliner_name} versions"
    fi

    # Extract the items array which contains the version list
    local versions
    versions=$(echo "$response" | jq -r '.items[]')

    if [ -z "$versions" ]; then
        die "No versions found for ${offliner_name}"
    fi

    echo "$versions"
}

# Fetch offliner definition for a specific version from Zimfarm API
fetch_offliner_version_definition() {
    local offliner_name="$1"
    local version="$2"
    local url="${OFFLINER_DEFINITIONS_BASE_URL}/offliners/${offliner_name}/${version}/spec"

    local response
    local http_code
    response=$(curl -s -w "\n%{http_code}" "$url")

    http_code=$(echo "$response" | tail -n1)
    response=$(echo "$response" | head -n1)

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        :
    else
        error_msg=$(echo "$response" | jq -r '.errors // .message // .detail // "Unknown error"' 2>/dev/null || echo "HTTP $http_code")
        die "Failed to fetch definition for ${offliner_name} version ${version} from ${url}: ${error_msg}"
    fi

    if ! echo "$response" | jq . >/dev/null 2>&1; then
        die "Invalid JSON received for ${offliner_name} version ${version}"
    fi

    echo "$response"
}

# Fetch and store all versions for an offliner from Zimfarm API
fetch_and_store_offliner_versions() {
    local offliner_name="$1"

    # Get all versions
    local versions
    versions=$(fetch_offliner_versions "$offliner_name")

    # Store each version in global array
    while IFS= read -r version; do
        if [ -n "$version" ]; then
            offliner_versions["${offliner_name}::${version}"]="$version"
        fi
    done <<< "$versions"

    # Verify at least one version was stored
    local found=false
    for key in "${!offliner_versions[@]}"; do
        if [[ "$key" == "${offliner_name}::"* ]]; then
            found=true
            break
        fi
    done

    if [ "$found" = false ]; then
        die "No versions found for ${offliner_name}"
    fi

    echo "Successfully stored versions for ${offliner_name}"
}

# Fetch definitions for all stored versions of an offliner
fetch_definitions_for_stored_versions() {
    local offliner_name="$1"

    echo "Fetching definitions for all ${offliner_name} versions..."

    # Iterate through stored versions and fetch definitions
    for key in "${!offliner_versions[@]}"; do
        if [[ "$key" == "${offliner_name}::"* ]]; then
            local version="${offliner_versions[$key]}"
            echo "Fetching definition for version: ${version}"

            local definition
            definition=$(fetch_offliner_version_definition "$offliner_name" "$version")
            offliner_definitions["$key"]=$(echo "$definition" | jq -c '.schema')
        fi
    done

    echo "Successfully fetched all definitions for ${offliner_name}"
}

register_offliner_via_api() {
    local offliner_id="$1"
    local config="${offliner_configs[$offliner_id]}"
    echo "Registering ${offliner_id} via API..."

    if [ -z "$config" ]; then
        die "No configuration found for offliner: ${offliner_id}"
    fi

    # Create the payload with offliner_id used as ci_secret_hash
    local payload
    payload=$(echo "$config" | jq --arg offliner_id "$offliner_id" '. + {"ci_secret_hash": $offliner_id, "offliner_id": $offliner_id}')

    local response
    local http_code
    response=$(curl -s -w "\n%{http_code}" -X 'POST' \
        "${ZIMFARM_BASE_API_URL}/offliners" \
        -H 'accept: application/json' \
        -H "Authorization: Bearer ${ZF_ADMIN_TOKEN}" \
        -H 'Content-Type: application/json' \
        -d "$payload")

    # Extract HTTP status code (last line)
    http_code=$(echo "$response" | tail -n1)
    # Extract response body (all lines except last)
    response=$(echo "$response" | head -n1)

    case "$http_code" in
        201)
            echo "Successfully registered ${offliner_id}"
            ;;
        409)
            echo "WARNING: Offliner ${offliner_id} already exists, skipping..."
            ;;
        *)
            local error_msg
            error_msg=$(echo "$response" | jq -r '.errors // .message // .detail // "Unknown error"' 2>/dev/null || echo "HTTP $http_code")
            die "Registration failed for ${offliner_id}: ${error_msg}"
            ;;
    esac
}

# Function to create offliner definition schema for a specific version
create_offliner_definition() {
    local offliner_id="$1"
    local version="$2"
    local spec="$3"

    if [ -z "$spec" ]; then
        die "No definition provided for offliner: ${offliner_id} version ${version}"
    fi

    echo "Creating definition for ${offliner_id} version ${version}..."

    # Create the payload for schema creation
    local payload
    payload=$(jq -n \
        --arg version "$version" \
        --arg ci_secret "$offliner_id" \
        --argjson spec "$spec" \
        '{version: $version, ci_secret: $ci_secret, spec: $spec}')

    # Create the schema via API
    local response
    local http_code
    response=$(curl -s -w "\n%{http_code}" -X 'POST' \
        "${ZIMFARM_BASE_API_URL}/offliners/${offliner_id}/versions" \
        -H 'accept: application/json' \
        -H "Authorization: Bearer ${ZF_ADMIN_TOKEN}" \
        -H 'Content-Type: application/json' \
        -d "$payload")

    # Extract HTTP status code (last line)
    http_code=$(echo "$response" | tail -n1)
    # Extract response body (all lines except last)
    response=$(echo "$response" | head -n1)

    case "$http_code" in
        201)
            echo "Successfully created schema for ${offliner_id} version ${version}"
            ;;
        409)
            echo "WARNING: Schema for ${offliner_id} version ${version} already exists, skipping..."
            ;;
        *)
            local error_msg
            error_msg=$(echo "$response" | jq -r '.errors // .message  // .detail // "Unknown error"' 2>/dev/null || echo "HTTP $http_code")
            die "Definition creation failed for ${offliner_id} version ${version}: ${error_msg}"
            ;;
    esac
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

echo "Admin token retrieved successfully"

# Setup offliner configurations for API registration
setup_offliner_configs

echo "Fetching offliner definitions..."

# Fetch and store all versions
for offliner in "${OFFLINERS[@]}"; do
    fetch_and_store_offliner_versions "$offliner"
done

# Fetch definitions for all stored versions
for offliner in "${OFFLINERS[@]}"; do
    fetch_definitions_for_stored_versions "$offliner"
done

echo "All offliner definitions fetched successfully"

# Register offliners and create definitions for all versions
for offliner in "${OFFLINERS[@]}"; do
    # Register the offliner once
    register_offliner_via_api "$offliner"

    # Create definitions for all versions
    for key in "${!offliner_versions[@]}"; do
        if [[ "$key" == "${offliner}::"* ]]; then
            version="${offliner_versions[$key]}"
            spec="${offliner_definitions[$key]}"
            create_offliner_definition "$offliner" "$version" "$spec"
        fi
    done
done

echo "All offliners registered via API successfully!"
