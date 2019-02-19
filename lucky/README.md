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

