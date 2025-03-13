# Database migrations

We use [YoYo database migrations](https://ollycope.com/software/yoyo/latest/) to manage
versioning the schema of both the development and production databases. The config file
for development is checked into this repo under `dev` and the config file for production
lives on the production box at `/data/wp1bot/db/yoyo.ini` (because it contains sensitive
database credentials).

All migrations are in the `migrations` folder. See the YoYo docs for more details on how
to add a new migration.

If you get an "unknown column 'foo'" or similar message when running nosetests, make sure
you've added the effects of the migration to the schema in wp10_test.up.sql. If you've
added a new table, also make sure it's torn down in wp10_test.down.sql.

See the sections in the main README on:

1. Migrating the dev database.
1. Updating production (section on running database migrations).
