#!/bin/bash


# Run the WP1 test suite.
#
# Automatically starts test containers if not running
# cleans dirty tables left behind by interrupted runs, then runs pytest.
#
# Usage:
#   ./scripts/util/run_tests.sh                    # run all tests
#   ./scripts/util/run_tests.sh wp1/tables_test.py # run specific tests

set -e

cd "$(dirname "$0")/../.."

DOCKER_DB_CONTAINER="wp1bot-test-db"
DOCKER_REDIS_CONTAINER="wp1bot-test-redis"

# Ensure test containers are running
if ! docker ps --format '{{.Names}}' | grep -q "^${DOCKER_DB_CONTAINER}$" || \
   ! docker ps --format '{{.Names}}' | grep -q "^${DOCKER_REDIS_CONTAINER}$"; then
  echo "Starting test containers..."
  docker compose -f docker-compose-test.yml up -d
  echo "Waiting for DB to be ready..."
  until docker exec "$DOCKER_DB_CONTAINER" mysql -u root -e "USE enwp10_test" 2>/dev/null; do
    sleep 1
  done
  echo "Containers are ready."
fi

# Clean dirty tables left behind by interrupted test runs
echo "Cleaning dirty tables..."
docker exec -i "$DOCKER_DB_CONTAINER" \
  mysql -u root enwp10_test < wp10_test.down.sql
docker exec -i "$DOCKER_DB_CONTAINER" \
  mysql -u root enwikip_test < wiki_test.down.sql
echo "Done."

# Run tests. Test configuration is constructed in code by conftest.py;
# no env file or WP1_ENV is needed.
pipenv run pytest "$@"
