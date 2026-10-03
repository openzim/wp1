# Docker images

Everything in WP1 runs in Docker, in both production and development. This
directory contains the Dockerfiles and support files for every image, one
subdirectory per image. The images are wired together by the compose files in
the repository root: `docker-compose.yml` (production),
`docker-compose-dev.yml` (development) and `docker-compose-test.yml` (backend
test databases).

Production images (built by CI on every release and published to ghcr.io):

- [`web/`](web/) — the Flask API server, served at
  [api.wp1.openzim.org](https://api.wp1.openzim.org).
- [`frontend/`](frontend/) — builds and serves the Vue frontend at
  [wp1.openzim.org](https://wp1.openzim.org).
- [`workers/`](workers/) — the RQ workers responsible for the asynchronous
  tasks of gathering the WP1 evaluation data and providing statistics and
  reports to the Wikipedia community, plus the cron scheduler
  (`cron_config.py`) that enqueues the recurring jobs.

Development-only images and services:

- [`dev-db/`](dev-db/README.md) — the development database, a drop-in
  replacement for the production database. See its README for migrating,
  seeding and updating the dev data.
- [`dev-frontend/`](dev-frontend/README.md) — runs the frontend with
  hot-reload, so no local Node.js install is needed.
- [`dev-workers/`](dev-workers/README.md) — a reduced version of the workers
  image that only materializes selections, and skips the production
  maintenance jobs.
- [`zimfarm/`](zimfarm/README.md) — a complete local
  [Zimfarm](https://github.com/openzim/zimfarm) (database, API, UI, worker)
  for developing ZIM file creation end to end.
- [`minio/`](minio/) — s3-compatible object storage used in development in
  place of the production S3 storage (Wasabi).

The `*.Dockerfile` symlinks in the repository root (`web.Dockerfile`,
`workers.Dockerfile`, `frontend.Dockerfile`) point into these subdirectories;
they are what the publish workflow builds, and they let each image's files
live here while keeping the repository root as the docker build context.
