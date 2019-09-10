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
is loaded and run through scripts in the top level directory, such as
`update.py`.

`requirements.txt` is a list of python dependencies in pip format that
need to be installed in a virtual env in order to run the code in this
directory.

The `wp10_test.*.sql` and `wiki_test.*.sql` files are rough
approximations of the schemas of the two databases that the library
interfaces with. They are used for unit testing.

## Installation

This code is targetted to and tested on Python 3. It may work
intermittently with Python 2.7, but that is not recommended.

### Creating your virtualenv

With Python 3, creating a virtualenv is a single easy command. It is
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

The tests expect a localhost MySQL instance on the default port, with
a user of 'root' and no password. You also need two databases:
`enwp10_test` and `enwikip_test`. They can use default settings and be
empty.

If you have that, and you've already installed the requirements above, you should be able to simply run:

```bash
nosetests
```

From this directory, to run the tests. If you'd like to use a
different MySQL user or non-default password for the tests, simply
edit `_setup_wp_one_db` and `_setup_wp_one_db` in `base_db_test.py`

### Populating the credentials module

The script needs access to the enwiki_p replica database, as well as
its own toolsdb application database. The credentials for these are on
toolforge in the replica.my.cnf file in the home directory. They need
to be formatted in a way that is consumable by the library and
pymysql. Look at `credentials.py.example` and create a copy called
`credentials.py` with the relevant information filled in. You will
also need english wikipedia API credentials.

## Running an application script

To run a script, you can simply run:

```bash
python3 enqueue-all.py
```

From the appropriate directory. However, this assumes that you have
followed the steps above and are inside the appropriate
virtualenv. For far-flung invocations of this script, you will need to
reference the python3 wrapper script in the virtualenv:

```bash
wikimedia_wp1_bot/venv/bin/python3 wikimedia_wp1_bot/update.py
```

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
