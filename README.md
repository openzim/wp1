# Wikipedia 1.0 engine

This directory contains the code of Wikipedia 1.0 supporting
software. More information about the Wikipedia 1.0 project can be
found [on the Wikipedia in
English](https://en.wikipedia.org/wiki/Wikipedia:Version_1.0_Editorial_Team).

[![build status](https://github.com/openzim/wp1/actions/workflows/workflow.yml/badge.svg)](https://github.com/openzim/wp1/actions?query=branch%3Amain)
[![codecov](https://codecov.io/gh/openzim/wp1/branch/main/graph/badge.svg)](https://codecov.io/gh/openzim/wp1)
[![CodeFactor](https://www.codefactor.io/repository/github/openzim/wp1/badge)](https://www.codefactor.io/repository/github/openzim/wp1)
[![Docker Web Build Status](https://img.shields.io/docker/cloud/build/openzim/wp1bot-web?label=docker%20web%20build)](https://cloud.docker.com/u/openzim/repository/docker/openzim/wp1bot-web)
[![Docker Worker Build Status](https://img.shields.io/docker/cloud/build/openzim/wp1bot-workers?label=docker%20workers%20build)](https://cloud.docker.com/u/openzim/repository/docker/openzim/wp1bot-workers)
[![Docker Frontend Build Status](https://img.shields.io/docker/cloud/build/openzim/wp1bot-frontend?label=docker%20frontend%20build)](https://cloud.docker.com/u/openzim/repository/docker/openzim/wp1bot-frontend)
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

`docker-compose-dev.yml` is a another docker file which sets up the test db
for python "nosetests" (unit tests). Run it similarly:

```bash
docker-compose -f docker-compose-test.yml up -d
```

The `*.dockerfile` symlinks allow for each docker image in this repository
to be more easily built on [Docker Hub](https://hub.docker.com/). See:

- https://hub.docker.com/repository/docker/openzim/wp1bot-frontend
- https://hub.docker.com/repository/docker/openzim/wp1bot-workers
- https://hub.docker.com/repository/docker/openzim/wp1bot-web

`openapi.yml` is a YAML file that describes the API of the `web` image
in [OpenAPI](https://swagger.io/specification/) format. If you visit
the [index of the API server](https://api.wp1.openzim.org) you will
get a swagger-ui documentation frontend that utilizes this file. It
is symlinked into the `wp1/web` directory.

The `wp10_test.*.sql` and `wiki_test.*.sql` files are rough
approximations of the schemas of the two databases that the library
interfaces with. They are used for unit testing.

## Installation

This code is targeted to and tested on Python 3.9.4.

### Creating your virtualenv

As of Python 3.3, creating a virtualenv is a single easy command. It is
recommmended that you run this command in the top level directory:

```bash
python3 -m venv venv
```

### Activating your virtualenv

To activate your virtualenv, run:

```bash
source venv/bin/activate
```

You should see your prompt change, with a `(venv)` appended to the front.

### Installing requirements

To install the requirements, make sure you are in your virtualenv as
explained above, then use the following command:

```bash
pip3 install -r requirements.txt
```

### Installing frontend requirements

To install the requirements for the frontend server, cd into `wp1-frontend`
and use:

```bash
yarn install
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
be destroyed after every test run. See the section "Running the tests".


### Running the tests

The tests require a MariaDB or MySQL instance to connect to in order to
verify various statements and logic. This database does not need to be
persistent and in fact part of the test setup and teardown is to recreate
a fresh schema for the test databases each time. You also will need two
databases in your server: `enwp10_test` and `enwikip_test`. They can use
default settings and be empty.

If you have that, and you've already installed the requirements above,
you should be able to simply run the following command from this
directory to run the tests:

```bash
nosetests
```

If you'd like to use a different MySQL user or non-default password for
the tests, you must edit `_setup_wp_one_db` and `_setup_wp_one_db` in
`base_db_test.py`.

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

## Migrating the dev database

The dev database will need to be migrated in the following circumstances:

1. In a clean checkout, the first time you run the `docker-compose` command above.
1. Anytime you remove/recreate the docker image
1. Anytime you or a team member adds a new migration

To migrate, cd to the `db/dev` directory and run the following command:

```bash
yoyo apply
```

The YoYo Migrations application will read the data in `db/dev/yoyo.ini` and attempt
to apply any necessary migrations to your database. If there are migrations to apply,
you will be prompted to confirm. If there are none, there will be no output.

More information on YoYo Migrations is available
[here](https://ollycope.com/software/yoyo/latest/).

## Starting the API server

Assuming you are in your Python virtualenv (described above) you can start
the API server with:

```bash
FLASK_DEBUG=1 FLASK_APP=wp1.web.app flask run
```

## Starting the web frontend

The web frontend can be started with the following command in the `wp1-frontend`
directory:

```bash
yarn serve
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
  - `sudo docker exec -ti wp1bot-workers yoyo -c /usr/src/app/db/production/yoyo.ini apply`

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
