# Dev Workers Dockerfile

This file represents a version of the workers image to be used in development. It only
starts a worker for materializing selection results from builders, and does not contain
any cron commands.

This image uses `supervisord-dev.conf` in the root directory, as opposed to the real
workers image which uses simply `supervisord.conf`.
