# Wikipedia 1.0 engine

This directory contains the code of Wikipedia 1.0 supporting
software. More information about the Wikipedia 1.0 project can be
found [on the Wikipedia in
English](https://en.wikipedia.org/wiki/Wikipedia:Version_1.0_Editorial_Team).

[![build status](https://github.com/openzim/wp1/actions/workflows/workflow.yml/badge.svg)](https://github.com/openzim/wp1/actions?query=branch%3Amain)
[![codecov](https://codecov.io/gh/openzim/wp1/branch/main/graph/badge.svg)](https://codecov.io/gh/openzim/wp1)
[![CodeFactor](https://www.codefactor.io/repository/github/openzim/wp1/badge)](https://www.codefactor.io/repository/github/openzim/wp1)
[![Doc](https://readthedocs.org/projects/wp1/badge/?style=flat)](https://wp1.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

## Contents

The `wp1` subdirectory includes code for updating the `enwp10`
database, specifically the `ratings` table (but also other
tables). The library code itself isn't directly runnable, but instead
is loaded and run in various docker images that are maintained in the
`docker` directory.

`requirements.txt` is a list of python dependencies in pip format that
need to be installed in a virtual env in order to run the library code.
Both the `web` and `workers` docker images use the same requirements,
though [Flask](https://www.palletsprojects.com/p/flask/) and its
dependencies are not utilized by the worker code.

`cron_config.py` defines the recurring jobs (nightly project update
enqueues, global articles table rebuild, assessment cache warming) that
are scheduled by RQ's built-in cron scheduler, run via supervisord inside
the workers image.

The `setup` directory contains a historical record of the database
schema used by the tool for what is referred to in code as the `wp10`
database. This file has been heavily edited, but should be able to be
used to re-create the `enwp10` database if necessary.

`wp1-frontend` contains the code for the Vue-CLI based frontend,
which is encapsulated and served from the `frontend` docker image.
See that directory for instructions on how to setup a development
environment for the frontend.

`conf.json` is a configuration file that is used by the `wp1`
library code.

`docker-compose.yml` is a file read by the `docker-compose`
[command](https://docs.docker.com/compose/) in order to generate the
graph of required docker images that represent the production environment.

`docker-compose-dev.yml` is a similar file which sets up a dev environment,
with Redis and a MariaDB server for the `enwp10` database. Through profiles like `zimfarm` and `zimfarm-worker`, you can start the Zimfarm containers required to execute a task.

`docker-compose-test.yml` is a another docker file which sets up the test db
for python "nosetests" (unit tests). Run it similarly:

```bash
docker compose -f docker-compose-test.yml up -d
```

The `*.dockerfile` symlinks allow for each docker image in this repository
(there are many) to be more easily organized.

`openapi.yml` is a YAML file that describes the API of the `web` image
in [OpenAPI](https://swagger.io/specification/) format. If you visit
the [index of the API server](https://api.wp1.openzim.org) you will
get a swagger-ui documentation frontend that utilizes this file. It
is symlinked into the `wp1/web` directory.

The `wp10_test.*.sql` and `wiki_test.*.sql` files are rough
approximations of the schemas of the two databases that the library
interfaces with. They are used for unit testing.

## Installation

This code is targeted to and tested on Python 3.12.0. For now, all development
has been on Linux, Other platforms may not be fully supported.

### Installing dependencies

WP1 uses [Pipenv](https://pipenv.pypa.io/en/latest/) to managed dependencies.
A `Pipfile` and `Pipfile.lock` are provided. You should have the pipenv tool
installed in your global Python install (not in a virtualenv):

```bash
pip3 install pipenv
```

Then you can use:

```bash
pipenv install --dev
```

Which will install the dependencies at the precise versions specified in the
`Pipfile.lock` file. Behind the scenes, Pipenv creates a virtualenv for you
automatically, which it keeps up to date when you run Pipenv commands. You
can use the `pipenv shell` command to start a shell using the environment,
which is similar to "activating" a virtualenv. You can also use `pipenv run`
to run arbitrary individual shell commands within that environment. In many
cases, it will be more convenient to use commands like `pipenv run pytest`
then actually spawning a subshell.

### Installing frontend requirements (optional)

**Note:** If you are using the docker-compose development environment, you do not
need to install Node.js or frontend dependencies locally. The frontend runs inside
a Docker container with hot-reload support. See the "Starting the web frontend"
section below.

If you prefer to run the frontend locally without Docker, it requires
[Node.js](https://nodejs.org/) version 22 to build and run. Once node is
installed, to install the requirements for the frontend server, cd into
`wp1-frontend` and use:

```bash
pnpm install
```

If you do not have pnpm, it can be enabled with:

```bash
corepack enable
```

### Docker

You will also need to have [Docker](https://www.docker.com/) on your system
in order to run the development server.

### Configuration (.env)

All backend configuration lives in a single schema in `wp1/config.py`,
read from environment variables. The committed
[`.env.example`](.env.example) is **generated from that schema** (run
`pipenv run python -m wp1.config` after changing it; CI fails on drift)
and documents every knob, its type, its default, and whether it is
required in production.

For development you usually need no configuration at all: the schema
defaults point at the services in `docker-compose-dev.yml`. To customize
values, copy `.env.example` to `.env` (gitignored) and edit it; the dev
containers pick it up via docker compose's `env_file`.

The main thing worth customizing is the `WIKIDB` section: the app reads
the enwiki_p replica database (referred to in the code as `wikidb`) on
Toolforge, and needs your Toolforge credentials to do so. If you are a
part of the toolforge `enwp10`
[project](https://tools.wmflabs.org/admin/tool/enwp10), you can find the
credentials on toolforge in the replica.my.cnf file in the tool's home
directory. This is not required for developing the frontend.

The production version of this code also requires English Wikipedia API
credentials (`API_USER`/`API_PASSWORD`) for automatically editing and
updating
[tables like this one](https://en.wikipedia.org/wiki/User:WP_1.0_bot/Tables/Project/Catholicism).
Currently, if your environment is DEVELOPMENT, jobs that utilize the API
to edit Wikipedia are disabled. There is no development wiki that gets
edited at this time.

Unit tests need no configuration or env files: the pytest bootstrap
(`conftest.py`) constructs the test configuration in code. See the next
section on running the tests.

### Running the backend (Python/pytest) tests

The backend/python tests require a MariaDB or MySQL instance to connect to in
order to verify various statements and logic. This database does not need to be
persistent and in fact part of the test setup and teardown is to recreate (destroy)
a fresh schema for the test databases each time. You also will need two databases
in your server: `enwp10_test` and `enwikip_test`. They can use default settings
and be empty. **If you've followed the steps under 'Development' below to
create a running dev database with docker-compose, you're all set.**

If you have that, and you've already installed the requirements above,
you should be able to simply run the following command from this
directory to run the tests:

```bash
./scripts/util/run_tests.sh
```

(or plain `pipenv run pytest` if the test containers are already up).

### Running the frontend (Cypress) integration tests

The Cypress tests are hermetic: every API call is stubbed with
`cy.intercept` (see `wp1-frontend/cypress/support/e2e.js` for the default
stubs and `wp1-frontend/cypress/fixtures/` for the response data), so you
don't need the Python backend, the dev database, or any Docker services.
All that's required is the frontend itself, served on port 5173. You can
either use the Vite dev server:

```bash
cd wp1-frontend
pnpm dev
```

or, to match CI exactly, the built bundle:

```bash
cd wp1-frontend
pnpm build --mode staging
python3 -m http.server 5173 --directory dist/
```

Then, in another terminal, run the tests:

```bash
cd wp1-frontend
pnpm exec cypress run
```

Or use `pnpm exec cypress open` for the interactive GUI, where you can
follow the prompts to run "Electron E2E tests".

# Development

For development, you will need to have Docker installed as explained above.

## Running docker-compose

There is a Docker setup for a development database. It lives in
`docker-compose-dev.yml`.

No configuration is needed before starting it: the defaults in
`wp1/config.py` already point at the in-network hostnames of these
services. If you want to customize anything (for example real `STORAGE`
credentials to materialize builder lists against an external S3), copy
`.env.example` to `.env` and edit it.

### Running parallel dev stacks (e.g. from git worktrees)

The easiest way is `./scripts/util/create_worktree.sh <branch>`, which creates the
worktree under `.worktrees/<branch>`, copies the untracked credentials and
`.env` files, writes a worktree-local `.env` with a unique project name,
suffix, and free port set (remapping the port-coupled app config values to
match), and offers to start the stack ("Start servers now? [Y/n]").

Manually, the mechanism is: all host ports, container names, and built
image tags in
`docker-compose-dev.yml` are parameterized with environment variables that
default to the values above, so a single checkout needs no configuration.
To run a second, fully independent stack (for example from another git
worktree), set `COMPOSE_PROJECT_NAME`, `WP1_SUFFIX`, and alternate ports for
the services you use:

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

### Setting up the development services

The dev stack has various containers which can be activated via various profiles. The `zimfarm` profile sets up a local zimfarm DB, API and UI.
The `zimfarm-worker` profile sets up a local zimfarm worker manager and receiver that stores the results/files of tasks.

If it is your first execution of the dev stack, you need to create offliners and a "virtual" worker in Zimfarm DB. Thus, you need to start the services without the worker profile until you register a worker.

You may need to install the `jq` tool with [these instructions](https://github.com/jqlang/jq/wiki/Installation).

#### Registering a worker

- Start the dev stack without a Zimfarm worker for now

  ```sh
  docker compose -f docker-compose-dev.yml --profile zimfarm up --pull always --build
  ```

  This starts the API, creates an admin user with username: `admin` and password `admin`

- Register offliners in the database

  ```sh
  cd docker/zimfarm
  ./create_offliners.sh
  ```

  This pulls the various versions of the mwoffliner definition schema from the Zimfarm API
  and registers the definition within your docker Zimfarm API. These definitions are
  necessary as they contain the latest parameters needed to run the `mwoffliner`
  scraper.

  In your `.env`, set the definition version to any of the versions pulled from the API. For example, if `1.17.2` was one of the downloaded definitions of the mwoffliner scraper:

  ```sh
  ZIMFARM_DEFINITION_VERSION=1.17.2
  ZIMFARM_IMAGE=ghcr.io/openzim/mwoffliner:1.17.2
  ```

  (These are also the schema defaults in `wp1/config.py`, so you only
  need to set them if you registered a different version.)

- Register a test Zimfarm worker

  ```sh
  cd docker/zimfarm
  ./create_worker.sh
  ```

  This generates an SSH key pair, registers a worker named `test-worker` with the Zimfarm API using the public key, and grants it the `wikimedia` context.

  The context grant matters: WP1 creates all of its recipes with the `wikimedia` context, and the Zimfarm scheduler only offers those tasks to workers holding that context. If your ZIM tasks sit forever in "requested" with an online worker, a missing context grant is the usual cause.

  The worker's resources (3 CPU, 20GB RAM, 20GB disk) and supported offliners are reported by the worker-manager container itself when it checks in — see the `ZIMFARM_*` environment variables in `docker-compose-dev.yml`. There is no worker user account: the current Zimfarm API authenticates workers purely by their SSH key.

- Restart the dev stack with a Zimfarm worker now
  ```sh
  docker compose -f docker-compose-dev.yml --profile zimfarm --profile zimfarm-worker \
  up -d
  ```

## Migrating and updating the dev database.

See the instructions in the associated [README file](https://github.com/openzim/wp1/blob/main/docker/dev-db/README.md)

## Starting the API server

The API server is included in the docker-compose-dev.yml graph and starts
automatically. It will be available at http://localhost:5000.

Running the app in Docker via `docker-compose-dev.yml` is the only
supported way to run it locally. The host-side toolchain (pipenv, pytest
via `./scripts/util/run_tests.sh`, and database migrations) still runs on
the host, against the docker-provided services.

## Starting the web frontend

The frontend is included in the docker-compose-dev.yml graph and starts
automatically with hot-reload support. It will be available at http://localhost:5173.

To start all development services including the frontend:

```bash
docker compose -f docker-compose-dev.yml up --build
```

Changes made to files in `wp1-frontend/src/` will be automatically reflected
in the browser without needing to restart the container.

### Running the frontend locally (alternative)

If you prefer to run the frontend locally instead of in Docker, you will need
Node.js installed. Then install the dependencies and start the dev server:

```bash
cd wp1-frontend
pnpm install
pnpm dev
```

## Development configuration

See [Configuration (.env)](#configuration-env) above: the schema defaults
in `wp1/config.py` already match the servers in `docker-compose-dev.yml`,
so no `.env` is needed to get started. To connect to a wiki replica
database on toolforge, set your credentials in the `WIKIDB_*` keys of
your `.env`. This is not required for developing the frontend.

## Development overlay

The API server has a built-in development overlay, currently used for manual
update endpoints. What this means is that the endpoints defined in
`wp1.web.dev.projects` are used with priority, instead of the production endpoints,
**only if the environment (`WP1_ENV`) is development, which is the default**. This is to allow
for easier manual and CI testing of the manual update page.

If you wish to test the manual update job with a real Wikipedia replica database
and RQ jobs, you will have to disable this overlay. The easiest way would be to
change the following line in wp1.web.app:

```
  if ENV == environment.Environment.DEVELOPMENT:
    # In development, override some project endpoints, mostly manual
    # update, to provide an easier env for developing the frontend.
    print('DEVELOPMENT: overlaying dev_projects blueprint. '
          'Some endpoints will be replaced with development versions')
    app.register_blueprint(dev_projects, url_prefix='/v1/projects')
```

to something like:

```
  if false:  # false while manually testing
    # In development, override some project endpoints, mostly manual
    ...
```

# Building/editing the docs

Documentation lives at [Read the Docs](https://wp1.readthedocs.io/en/latest/). It is
built using [mkdocs](https://www.mkdocs.org/). The Read the Docs site automatically
monitors the WP1 github HEAD and re-builds the documentation on every push. CI also
runs `mkdocs build --strict` on every pull request, so a broken docs build fails the
build before it reaches Read the Docs.

## Local docs

If you are editing the docs and would like to view them locally before pushing:

```bash
$ cd docs
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cd ..
$ mkdocs serve
```

The `serve` command should print out the port to view the docs at, likely localhost:8000.

# Updating production

Deploys are done with `scripts/wp1/deploy.sh`, run from a local checkout:

```bash
./scripts/wp1/deploy.sh
```

This deploys the current `origin/main`. It requires push access to this
repository and ssh access (with sudo) to the production box,
`mwcurator-b.mwoffliner.eqiad1.wikimedia.cloud` (override with the
`WP1_DEPLOY_HOST` environment variable; see
[SSH access](#ssh-access-to-the-production-box) below for one-time
setup). The script:

- Pushes `origin/main` to the `release` branch (a plain, non-forced
  push: if `release` has diverged from `main` the push is rejected and
  a human needs to sort it out). This triggers the
  [publish workflow](https://github.com/openzim/wp1/actions/workflows/publish.yml),
  which builds and pushes the `wp1-workers`, `wp1-web` and
  `wp1-frontend` docker images.
- Runs `scripts/wp1/deploy-remote.sh` on the production box (after a
  `git pull` there, so the remote script is the version being
  deployed), which:
  - Warns and asks for confirmation if `.env.example` changed since the
    last deploy, since the production env file `/data/wp1bot/wp1.env`
    (consumed by `docker-compose.yml` via `env_file`) is managed by hand
    and probably needs a matching update.
  - Waits for all three images tagged `sha-<short sha>` for the exact
    commit being deployed to appear on ghcr.io. Deploying by the
    immutable sha tag (instead of pulling the moving `release` tag)
    guarantees a consistent image set; the three build jobs finish at
    different times, so `release` can briefly point at a mixed set.
  - Pulls the three images, re-tags them locally as `release` (the tag
    `docker-compose.yml` uses), and runs `docker compose up -d`. Only
    those three images are ever pulled -- never `docker compose pull`,
    which would also refresh infrastructure images like the pinned
    redis (see [Redis persistence](#redis-persistence) below).
  - Applies database migrations:
    `yoyo -c /usr/src/app/db/production/yoyo.ini apply --batch` in the
    workers container.
  - Verifies that the containers are running and that
    https://api.wp1.openzim.org and https://wp1.openzim.org respond.

`scripts/wp1/deploy-remote.sh` can also be run by hand on the box
(`cd /data/code/wp1 && sudo ./scripts/wp1/deploy-remote.sh <full git sha>`)
if the local half already pushed `release` but the remote half failed
or was interrupted; it is safe to re-run.

## SSH access to the production box

The production box is a [Wikimedia Cloud VPS](https://wikitech.wikimedia.org/wiki/Portal:Cloud_VPS)
instance in the `mwoffliner` project. It is not reachable directly from
the internet; ssh goes through the Cloud VPS bastion. One-time setup
(see [Help:Accessing Cloud VPS instances](https://wikitech.wikimedia.org/wiki/Help:Accessing_Cloud_VPS_instances)
for the full guide):

1. [Create a Wikimedia developer account](https://idm.wikimedia.org/signup/)
   and [upload your public SSH key](https://idm.wikimedia.org/keymanagement/).
2. Ask an existing member to add you to the `mwoffliner` Cloud VPS project.
3. Add the bastion jump host to your `~/.ssh/config` (use your _shell_
   username from idm.wikimedia.org, which may differ from your account
   username):

   ```
   Host *.wikimedia.cloud
     User <your-shell-name>
     ProxyJump bastion.wmcloud.org:22
   ```

Then `ssh mwcurator-b.mwoffliner.eqiad1.wikimedia.cloud` should log you
in without a password, which is what `scripts/wp1/deploy.sh` needs.

## Redis persistence

Redis holds the RQ queue state and the only copy of the rolling 7-day
article assessment log history (used to generate the on-wiki log pages).
The `redis` service therefore stores its data in the `redis-data` volume
and its image tag is pinned in `docker-compose.yml`. To upgrade Redis,
bump the tag deliberately and deploy normally; the volume preserves the
data across the container recreation. Do not deploy with an unpinned
`redis` image: a surprise upstream image update recreates the container,
and before the volume existed that meant losing the entire keyspace
(this happened on 2026-08-01 and overwrote hundreds of on-wiki log pages
with false "no logs" notices; see
[issue #1244](https://github.com/openzim/wp1/issues/1244)).

# Rolling back production

In addition to the moving `release` tag, every push to the `release`
branch publishes each image with two immutable tags: `release-<n>`
(where `<n>` is the run number of the publish workflow) and
`sha-<git sha>`. The available versions for each image are listed on
its GitHub packages page:

- https://github.com/openzim/wp1/pkgs/container/wp1-workers/versions
- https://github.com/openzim/wp1/pkgs/container/wp1-web/versions
- https://github.com/openzim/wp1/pkgs/container/wp1-frontend/versions

To roll back a bad deploy, run (from a local checkout):

```bash
./scripts/wp1/deploy.sh --rollback release-141   # or e.g. sha-73ed612
```

This runs `scripts/wp1/deploy-remote.sh --rollback <tag>` on the box, which
pulls that version of each image, re-tags it locally as `release` (no
registry login or push is required, the local tag is what docker
compose uses), and recreates the containers. A successful deploy prints
the sha tag of the version it replaced, which is the tag to pass here.

Note that the next normal deploy rolls forward again. Rolling back
database migrations is deliberately not automated; if the deploy being
rolled back included migrations, roll those back by hand on the box:

- `sudo docker exec -ti -e PYTHONPATH=. wp1bot-workers yoyo -c /usr/src/app/db/production/yoyo.ini rollback`

# Pre-commit hooks

This project is configured to use git pre-commit hooks managed by the
Python program `pre-commit` ([website](https://pre-commit.com/)). Pre-
commit checks let us ensure that the code is properly formatted with
[Black](https://github.com/psf/black) amongst other things.

If you've installed the requirements for this repository, the pre-commit
binary should be available to you. To install the hooks, use:

```bash
pre-commit install
```

Then, when you try to commit a change that would fail pre-commit, you get:

```
(venv) host:wikimedia_wp1_bot audiodude$ git commit -am 'Test commit'
Trim Trailing Whitespace.................................................Passed
Fix End of Files.........................................................Passed
black....................................................................Failed
hookid: black
```

From there, the pre-commit hook will have modified and thus unstaged some or all
of the files you were trying to commit. Look through the changes to make sure
they are sane, then re-add them with git add, before trying your commit again.

# License

GPLv2 or later, see [LICENSE](LICENSE) for more details.
