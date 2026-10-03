# Dev Workers Dockerfile

This file represents a version of the workers image to be used in development. It only
starts a worker for materializing selection results from builders, and does not run
the daily production maintenance jobs (those are gated to production in
`cron_config.py`).

This image uses `supervisord-dev.conf` in the root directory, as opposed to the real
workers image which uses simply `supervisord.conf`.

Configuration comes from the schema defaults in `wp1/config.py` (which
already point at the dev docker services) plus an optional `.env` file in
the repository root, consumed via the `env_file` directive in
`docker-compose-dev.yml`. See `.env.example` for every available knob.
