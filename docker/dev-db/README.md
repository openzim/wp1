This docker container is for a copy of the WP1 database to be used in the
DEVELOPMENT environment. It is a drop-in replacement for the production
database hosted on Toolforge, and fulfills the same functionality in the app.

## Migrating the dev database

The dev database will need to be migrated in the following circumstances:

1. In a clean checkout, the first time you run the `docker-compose` command for
   the dev docker graph.
1. Anytime you remove/recreate the docker image
1. Anytime you or a team member adds a new migration

To migrate, cd to the `db/dev` directory and run the following command:

```bash
PYTHONPATH=$PYTHONPATH:../.. yoyo apply
```

The `PYTHONPATH` environment variable is necessary because some of the migrations
imports wp1 code in order to complete the migration.

The YoYo Migrations application will read the data in `db/dev/yoyo.ini` and attempt
to apply any necessary migrations to your database. If there are migrations to apply,
you will be prompted to confirm. If there are none, there will be no output.

More information on YoYo Migrations is available
[here](https://ollycope.com/software/yoyo/latest/).

## Updating the dev database dump

After migrations have been applied to production and are stable, it makes sense
to "permanently" apply them to the dev database dump so that the migrations do
not have to be run everytime the dev database is recreated.

As part of this process, you will create a MySQL dump file of the dev database.
It is important to recognize that all data from your dev database will be included
in this dump, and available on Github. Please make sure there isn't any sensitive or
personally identifiable information included.

### Setup Git LFS

The database dump file is attached to the git repository using Git LFS, so that the
rather large file does not need to be stored alongside the normal git repository.
If you haven't already, set up [Git LFS](https://git-lfs.github.com/) and make sure
that when you run the following command:

```bash
head docker/dev-db/enwp10_dev.dump.sql
```

You see:

```
head docker/dev-db/enwp10_dev.dump.sql
CREATE DATABASE `enwp10_dev` CHARACTER SET = "utf8mb4" COLLATE = "utf8mb4_unicode_ci";
USE enwp10_dev;

-- MySQL dump 10.13  Distrib 8.0.30, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: enwp10_dev
-- ------------------------------------------------------
-- Server version       5.5.5-10.1.48-MariaDB-1~bionic

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
```

If you see something about SHA256 hashes, you may have set up Git LFS but not actually
checked out the db dump file with it. Try a `git restore` on the dump file.

### Getting a clean copy of the dev database

Run the following commands to stop and destroy your dev database:

```bash
docker stop wp1bot-db-dev
docker rm wp1bot-db-dev
```

Then you can load a fresh copy with the docker compose command for development.

```bash
docker-compose -f docker-compose-dev.yml up -d
```

Next, apply the migrations using the steps above.

After that, cd into the directory where the database dump is store and create a new
dump:

```bash
cd docker/dev-db
mysqldump --column-statistics=0 -h 127.0.0.1 -P 6300 --user=root -pwikipedia --lock-tables --single-transaction --quick enwp10_dev > enwp10_dev.dump.sql
```

Finally, we must add CREATE and USE database commands to the top of the dump so that our
actual database is created when the dev db server starts.

```bash
echo -e "CREATE DATABASE \`enwp10_dev\` CHARACTER SET = \"utf8mb4\" COLLATE = \"utf8mb4_unicode_ci\";\nUSE enwp10_dev;\n\n$(cat enwp10_dev.dump.sql)" > enwp10_dev.dump.sql
```

Once you're done, commit the file and push it to Github as normal.
