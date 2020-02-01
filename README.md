# Wikipedia 1.0 engine

This directory contains the code of Wikipedia 1.0 supporting
software. More information about the Wikipedia 1.0 project can be
found [on the Wikipedia in
English](https://en.wikipedia.org/wiki/Wikipedia:Version_1.0_Editorial_Team).

[![Build Status](https://travis-ci.com/openzim/wp1.svg?branch=master)](https://travis-ci.com/openzim/wp1)
[![codecov](https://codecov.io/gh/openzim/wp1/branch/master/graph/badge.svg)](https://codecov.io/gh/openzim/wp1)
[![CodeFactor](https://www.codefactor.io/repository/github/openzim/wp1/badge)](https://www.codefactor.io/repository/github/openzim/wp1)
[![Docker Web Build Status](https://img.shields.io/docker/cloud/build/openzim/wp1bot-web?label=docker%20web%20build)](https://cloud.docker.com/u/openzim/repository/docker/openzim/wp1bot-web)
[![Docker Worker Build Status](https://img.shields.io/docker/cloud/build/openzim/wp1bot-workers?label=docker%20workers%20build)](https://cloud.docker.com/u/openzim/repository/docker/openzim/wp1bot-workers)
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
database. This file has been heavily edited from its mysqldump roots
and cannot be directly run without errors.

`wp1-frontend` contains the code for the Vue-CLI based frontend,
which is encapsulated and served from the `frontend` docker image.
See that directory for instructions on how to setup a development
environment for the frontend.

`conf.json` is a configuration file that is used by the `wp1`
library code.

`docker-compose.yml` is a file read by the `docker-compose`
[command](https://docs.docker.com/compose/) in order to generate the
graph of required docker images that represent the production environment.

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

This code is targetted to and tested on Python 3.7.5.

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

### Running the tests

The tests expect a localhost MariaDB or MySQL instance on the default
port, with a user of 'root' and no password. You also need two databases:
`enwp10_test` and `enwikip_test`. They can use default settings and be
empty.

If you have that, and you've already installed the requirements above,
you should be able to simply run the following command from this
directory to run the tests:

```bash
nosetests
```

If you'd like to use a different MySQL user or non-default password for
the tests, you must edit `_setup_wp_one_db` and `_setup_wp_one_db` in
`base_db_test.py`.

### Populating the credentials module

The script needs access to the enwiki_p replica database (referred to
in the code as `wikidb`), as well as its own toolsdb application database
(referred to in the code as `wp10db`). If you are a part of the toolforge
`enwp10` [project](https://tools.wmflabs.org/admin/tool/enwp10), you can
find the credentials for these on toolforge in the replica.my.cnf file in
the tool's home directory. They need to be formatted in a way that is
consumable by the library and pymysql. Look at `credentials.py.example`
and create a copy called `credentials.py` with the relevant information
filled in. The production version of this code also requires Englis Wikipedia
API credentials for automatically editing and updating
[tables like this one](https://en.wikipedia.org/wiki/User:WP_1.0_bot/Tables/Project/Catholicism).
There is currently no way to disable the API editing portion of the tool.

## Updating production

- Log in to the box that contains the production docker images. It is
  called wp1.
- `cd /data/code/wikimedia_wp1_bot/`
- `sudo git pull origin master`
- Pull the docker images from docker hub:
  - `docker pull openzim/wp1bot-workers`
  - `docker pull openzim/wp1bot-web`
  - `docker pull openzim/wp1bot-frontend`
- Re-run docker-compose: `docker-compose up -d`

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
