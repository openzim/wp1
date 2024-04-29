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

The `cron` directory contains wrapper scripts for cron jobs that are
run [inside the workers image](https://github.com/openzim/wp1/blob/master/docker/workers/Dockerfile#L15).

The `setup` directory contains a historical record of the database
schema used by the tool for what is refered to in code as the `wp10`
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
with Redis and a MariaDB server for the `enwp10` database. Use it like so

```bash
docker-compose -f docker-compose-dev.yml up -d
```

`docker-compose-test.yml` is a another docker file which sets up the test db
for python "nosetests" (unit tests). Run it similarly:

```bash
docker-compose -f docker-compose-test.yml up -d
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
has been on Linux, use other platforms at your own risk.

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

### Installing frontend requirements

The frontend requires [Node.js](https://nodejs.org/) version 18 to build and
run. Once node is installed, to install the requirements for the frontend
server, cd into `wp1-frontend` and use:

```bash
yarn install
```

If you do not have yarn, it can be installed with:

```bash
npm i -g yarn
```

### Docker

You will also need to have [Docker](https://www.docker.com/) on your system
in order to run the development server.

### Populating the credentials module

The script needs access to the enwiki_p replica database (referred to
in the code as `wikidb`), as well as its own toolsdb application database
(referred to in the code as `wp10db`). If you are a part of the toolforge
`enwp10` [project](https://tools.wmflabs.org/admin/tool/enwp10), you can
find the credentials for these on toolforge in the replica.my.cnf file in
the tool's home directory. They need to be formatted in a way that is
consumable by the library and pymysql. Look at `credentials.py.example`
and create a copy called `credentials.py` with the relevant information
filled in. The production version of this code also requires English Wikipedia
API credentials for automatically editing and updating
[tables like this one](https://en.wikipedia.org/wiki/User:WP_1.0_bot/Tables/Project/Catholicism).
Currently, if your environment is DEVELOPMENT, jobs that utilize the API
to edit Wikipedia are disabled. There is no development wiki that gets edited
at this time.

The "development" credentials files, `credentials.py.dev` and
`credentials.py.dev.example` are for running the docker graph of development
resources. They are copied into the docker container that is run when using
`docker-compose-dev.yml`.

The `credentials.py` file proper also contains a section for TEST database
credentials. These are used in unit tests. If you use the database provided
in `docker-compose-test.yml` you can copy these directly from the example
file. However, you are free to provide your own test database that will
be destroyed after every test run. See the next section on running the tests.

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
pipenv run pytest
```

### Running the frontend (Cypress) integration tests

For frontend tests, you need to have a full working local development
environment. You should follow the steps in 'Installation' above, as well as the
steps in 'Development' below. Your frontend should be running on port 5173 (the
default) and the backend should be on port 5000 (also the default).

To run the tests:

```bash
cd wp1-frontend
$(yarn bin)/cypress run
```

Then follow the GUI prompts to run "Electron E2E tests".

# Development

For development, you will need to have Docker installed as explained above.

## Running docker-compose

There is a Docker setup for a development database. It lives in
`docker-compose-dev.yml`.

Before you run the docker-compose command below, you must copy the file
`wp1/credentials.py.dev.example` to `wp1/credentials.py.dev` and fill out the
section for `STORAGE`, if you wish to properly materialize builder lists into
backend selections.

After that is done, use the following command to run the dev environment:

```bash
docker-compose -f docker-compose-dev.yml up -d
```

## Migrating and updating the dev database.

See the instructions in the associated [README file](https://github.com/openzim/wp1/blob/main/docker/dev-db/README.md)

## Starting the API server

Using pipenv, you can start the API server with:

```bash
pipenv run flask --app wp1.web.app --debug run
```

## Starting the web frontend

Assuming you've installed the frontend deps (`yarn install`), the web frontend
can be started with the following command in the `wp1-frontend` directory:

```bash
yarn dev
```

## Development credentials.py

The DEVELOPMENT section of credentials.py.example is already filled out with
the proper values for the servers listed in docker-compose-dev.yml. You should
be able to simply copy it to credentials.py.

If you wish to connect to a wiki replica database on toolforge, you will need
to fill out your credentials in WIKIDB section. This is not required for
developing the frontend.

## Development overlay

The API server has a built-in development overlay, currently used for manual
update endpoints. What this means is that the endpoints defined in
`wp1.web.dev.projects` are used with priority, instead of the production endpoints,
**only if the credentials.py ENV == Environment.DEVELOPMENT**. This is to allow
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
monitors the WP1 github HEAD and re-builds the documentation on every push.

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

- Push to the release branch of the github repository:
  - `git checkout main`
  - `git pull origin main`
  - `git checkout release`
  - `git merge main`
  - `git push origin release`
- Wait for the release images [to be built](https://github.com/openzim/wp1/actions/workflows/publish.yml)
- Log in to the box that contains the production docker images. It is
  called mwcurator.
- `cd /data/code/wp1/`
- `sudo git pull origin main`
- Pull the docker images from docker hub:
  - `sudo docker pull ghcr.io/openzim/wp1-workers:release`
  - `sudo docker pull ghcr.io/openzim/wp1-web:release`
  - `sudo docker pull ghcr.io/openzim/wp1-frontend:release`
- Run docker-compose to bring the production images online.
  - `sudo docker-compose up -d`
- Run the production database migrations in the worker container:
  - `sudo docker exec -ti -e PYTHONPATH=app wp1bot-workers yoyo -c /usr/src/app/db/production/yoyo.ini apply`

# Pre-commit hooks

This project is configured to use git pre-commit hooks managed by the
Python program `pre-commit` ([website](https://pre-commit.com/)). Pre-
commit checks let us ensure that the code is properly formatted with
[yapf](https://github.com/google/yapf) amongst other things.

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
yapf.....................................................................Failed
hookid: yapf
```

From there, the pre-commit hook will have modified and thus unstaged some or all
of the files you were trying to commit. Look through the changes to make sure
they are sane, then re-add them with git add, before trying your commit again.

# License

GPLv2 or later, see [LICENSE](LICENSE) for more details.
