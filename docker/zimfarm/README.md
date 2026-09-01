# Local Zimfarm for development

WP1 creates ZIM files by scheduling recipes/tasks on the
[Zimfarm](https://github.com/openzim/zimfarm). This directory contains the
config and helper scripts for running a complete local Zimfarm inside the dev
docker graph, so that ZIM creation can be developed and tested end to end
without touching the production Zimfarm.

The containers are activated through docker compose profiles in
`docker-compose-dev.yml`:

- The `zimfarm` profile starts the Zimfarm database (postgres), API, and UI.
- The `zimfarm-worker` profile starts a Zimfarm worker manager and a task
  receiver that stores the results/files of completed tasks.

None of this is required for ordinary WP1 development; you only need it when
working on ZIM file creation.

## First-time setup: registering offliners and a worker

On the first run, the Zimfarm database is empty: it has no offliner
definitions and no registered workers. Start the stack _without_ the worker
profile, register both, then restart with the worker.

You may need to install the `jq` tool with
[these instructions](https://github.com/jqlang/jq/wiki/Installation).

- Start the dev stack without a Zimfarm worker for now

  ```sh
  docker compose -f docker-compose-dev.yml --profile zimfarm up --pull always --build
  ```

  This starts the API, creates an admin user with username: `admin` and
  password `admin`

- Register offliners in the database

  ```sh
  cd docker/zimfarm
  ./create_offliners.sh
  ```

  This pulls the various versions of the mwoffliner definition schema from the
  Zimfarm API and registers the definition within your docker Zimfarm API.
  These definitions are necessary as they contain the latest parameters needed
  to run the `mwoffliner` scraper.

  In your `.env`, set the definition version to any of the versions pulled
  from the API. For example, if `1.17.2` was one of the downloaded definitions
  of the mwoffliner scraper:

  ```sh
  ZIMFARM_DEFINITION_VERSION=1.17.2
  ZIMFARM_IMAGE=ghcr.io/openzim/mwoffliner:1.17.2
  ```

  (These are also the schema defaults in `wp1/config.py`, so you only need to
  set them if you registered a different version.)

- Register a test Zimfarm worker

  ```sh
  cd docker/zimfarm
  ./create_worker.sh
  ```

  This generates an SSH key pair, registers a worker named `test-worker` with
  the Zimfarm API using the public key, and grants it the `wikimedia` context.

  The context grant matters: WP1 creates all of its recipes with the
  `wikimedia` context, and the Zimfarm scheduler only offers those tasks to
  workers holding that context. If your ZIM tasks sit forever in "requested"
  with an online worker, a missing context grant is the usual cause.

  The worker's resources (3 CPU, 20GB RAM, 20GB disk) and supported offliners
  are reported by the worker-manager container itself when it checks in — see
  the `ZIMFARM_*` environment variables in `docker-compose-dev.yml`. There is
  no worker user account: the current Zimfarm API authenticates workers purely
  by their SSH key.

- Restart the dev stack with a Zimfarm worker now
  ```sh
  docker compose -f docker-compose-dev.yml --profile zimfarm --profile zimfarm-worker \
  up -d
  ```

## Caveat: parallel dev stacks

The Zimfarm UI config (`zimfarm_ui_dev/config.json`) hardcodes the API URL
`http://localhost:8004`, so a second dev stack's Zimfarm UI (see
[parallel dev stacks](../../scripts/util/README.md)) won't reach its remapped
API without editing that file in the worktree.
