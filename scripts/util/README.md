# Development utility scripts

- [`run_tests.sh`](run_tests.sh) — run the backend test suite. Starts the test
  containers (`docker-compose-test.yml`) if they aren't already running,
  cleans dirty tables left behind by interrupted runs, then runs
  `pipenv run pytest` (arguments are forwarded, e.g.
  `./scripts/util/run_tests.sh wp1/tables_test.py`).
- [`check_types.sh`](check_types.sh) — run `ty` type checking against the
  subset of files that are fully annotated (the list lives in the script
  itself and is the single source of truth; CI invokes it directly).
- [`seed-dev-selections.py`](seed-dev-selections.py) — seed the dev database
  with test Selection data; see
  [docker/dev-db/README.md](../../docker/dev-db/README.md#seeding-test-selection-data).
- [`create_worktree.sh`](create_worktree.sh) — set up a git worktree with its
  own parallel dev stack, described below.

## Running parallel dev stacks (e.g. from git worktrees)

The easiest way is `./scripts/util/create_worktree.sh <branch>`, which creates
the worktree under `.worktrees/<branch>`, writes a worktree-local `.env`
(based on the main checkout's `.env`, if present) with a unique project name,
suffix, and free port set (remapping the port-coupled app config values to
match), and offers to start the stack ("Start servers now? [Y/n]").

Manually, the mechanism is: all host ports, container names, and built image
tags in `docker-compose-dev.yml` are parameterized with environment variables
that default to the standard values, so a single checkout needs no
configuration. To run a second, fully independent stack (for example from
another git worktree), set `COMPOSE_PROJECT_NAME`, `WP1_SUFFIX`, and alternate
ports for the services you use:

```bash
export COMPOSE_PROJECT_NAME=wp1-dev-b
export WP1_SUFFIX=-b            # suffix for container names and image tags
export WP1_REDIS_PORT=9737      # default 9736
export WP1_DB_PORT=6301         # default 6300
export WP1_MINIO_PORT=9002      # default 9000
export WP1_MINIO_CONSOLE_PORT=9003  # default 9001
export WP1_WEB_PORT=5001        # default 5000
export WP1_FRONTEND_PORT=5274   # default 5173
docker compose -f docker-compose-dev.yml up --build
```

These can also go in the (gitignored) `.env` file of the worktree, which
docker compose reads automatically. The zimfarm profile ports are likewise
configurable via `WP1_ZIMFARM_DB_PORT` (2345), `WP1_ZIMFARM_API_PORT` (8004)
and `WP1_ZIMFARM_UI_PORT` (8003).

Notes:

- Each stack gets its own network and volumes (`<project>_minio-data`), so
  minio bucket setup runs per stack, and each stack has its own dev database.
- The backend is referred to by the in-network hostname `wp1bot-web-dev`
  (the `CLIENT_BACKEND_URL` default in `wp1/config.py`); this keeps
  working in a suffixed stack via a network alias, no changes needed.
- Caveat: the zimfarm UI config
  (`docker/zimfarm/zimfarm_ui_dev/config.json`) hardcodes the API URL
  `http://localhost:8004`, so a second stack's zimfarm UI won't reach its
  remapped API without editing that file in the worktree.
