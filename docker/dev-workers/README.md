# Dev Workers Dockerfile

This file represents a version of the workers image to be used in development. It only
starts a worker for materializing selection results from builders, and does not contain
any cron commands.

This image uses `supervisord-dev.conf` in the root directory, as opposed to the real
workers image which uses simply `supervisord.conf`.

The image requires that the `credentials.py.dev.example` file in the `wp1` directory
be filled out and copied to `credentials.py.dev`. More info is in the .example file.
If this is not done before the `docker-compose-dev.yml` file is run, `credentials.py.dev`
will be created as a directory and will have to be removed and replaced with the actual
file.
