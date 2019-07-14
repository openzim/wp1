# WP1 bot Python rewrite: lucky

This directory contains the code for a Python rewrite of the original Perl codebase
of the WP1 bot. The rewrite is codenamed 'lucky'. All of the code for the rewrite
exists in this directory. No files outside of this directory were touched as part of
the rewrite.

## Contents

The `lucky` subdirectory of the same name contains all of the library code that is
currently rewritten. As of this writing (2019-02-18), that includes code for updating
the enwp10 database, specifically the `ratings` table (but also other tables). The
library code itself isn't directly runnable, but instead is loaded and run through
scripts in the top level directory, such as `update_all.py` and `update_catholicism.py`

`conf.json` in this directory is a configuration file that operates similarly to
`backend/example.wp10.conf` in the main directory.

`requirements.txt` is a list of python dependencies in pip format that need to be
installed in a virtual env in order to run the code in this directory.

As already mentioned, the `update_*` scripts are actual "binaries" that use the library
code to perform useful actions on the enwp10 database.

The `wp10_test.*.sql` and `wiki_test.*.sql` files are rough approximations of the
schemas of the two databases that the library interfaces with. They are used for unit
testing.

## Installation

This code is targetted to and tested on Python 3, specifically Python 3.4.3 which is the
version that was available on toolforge at the time it was written. It may work
intermittently with Python 2.7, but that is not recommended.

### Creating your virtualenv

With Python 3, creating a virtualenv is a single easy command. It is recommmended that you
run this command in this directory:

`$ python3 -m venv venv`

If you are on wikimedia toolforge and get the following message:

`The virtual environment was not created successfully because ensurepip is not
available.`

Try running in a kubernetes session first:

`$ webservice --backend=kubernetes python shell`

### Activating your virtualenv

To activate your virtualenv, run:

`$ source venv/bin/activate`

You should see your prompt change, with a `(venv)` appended to the front.

### Installing requirements

To install the requirements, make sure you are in your virtualenv as explained above, then
use the following command:

`$ pip3 install -r requirements.txt`

### Running the tests

The tests expect a localhost MySQL instance on the default port, with a user of 'root' and no password. You also need two databases: `enwp10_test` and `enwikip_test`. They can use default settings and be empty.

If you have that, and you've already installed the requirements above, you should be able to simply run:

`$ nosetests`

From this directory, to run the tests. If you'd like to use a different MySQL user or non-default password for the tests, simply edit `_setup_wp_one_db` and `_setup_wp_one_db` in lucky/base_db_test.py

### Populating the credentials module

The script needs access to the enwiki_p replica database, as well as its own toolsdb
application database. The credentials for these are on toolforge in the replica.my.cnf file
in the home directory. They need to be formatted in a way that is consumable by the library
and pymysql. Look at `lucky/credentials.py.example` and create a copy called
`lucky/credentials.py` with the relevant information filled in. You will also need english
wikipedia API credentials.

## Running an application script

To run a script, such as `update_catholicism.py`, you can simply run:

`$ python3 update_catholicism.py`

From the appropriate directory. However, this assumes that you have followed the steps above
and are inside the appropriate virtualenv. For far-flung invocations of this script, you will
need to reference the python3 wrapper script in the virtualenv:

`$ wikimedia_wp1_bot/lucky/venv/bin/python3 wikimedia_wp1_bot/lucky/update_catholicism.py`
