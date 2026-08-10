# Deployment & Docker Docs

> 45 nodes

## Key Concepts

- **credentials.py Module (env-specific credentials)** (9 connections) — `README.md`
- **Wikipedia 1.0 Engine (WP1) Overview** (8 connections) — `README.md`
- **Production Docker Compose Stack** (8 connections) — `docker-compose.yml`
- **Production Service: web (wp1-web:release, api.wp1.openzim.org)** (6 connections) — `docker-compose.yml`
- **Contributing Guide for WP1** (5 connections) — `CONTRIBUTING.md`
- **Dev Service: dev-workers (materialize workers)** (5 connections) — `docker-compose-dev.yml`
- **Dev Database Container (drop-in replacement for Toolforge DB)** (5 connections) — `docker/dev-db/README.md`
- **Production Deployment Process (release branch to mwcurator)** (4 connections) — `README.md`
- **YoYo Database Migrations** (4 connections) — `db/README.md`
- **Production Service: redis (pinned 8.10 + redis-data volume)** (4 connections) — `docker-compose.yml`
- **Production Service: workers (wp1-workers:release)** (4 connections) — `docker-compose.yml`
- **WP1 Docker Images Overview (workers, web, frontend, dev-db, dev-workers)** (4 connections) — `docker/README.md`
- **Dev Workers Docker Image (materialize-only)** (4 connections) — `docker/dev-workers/README.md`
- **CI Job: python-tests (pytest + MariaDB + Redis services)** (3 connections) — `.github/workflows/ci.yml`
- **Publish Docker Images Workflow (release branch)** (3 connections) — `.github/workflows/publish.yml`
- **Testing Requirements (90%+ coverage, mocked network)** (3 connections) — `CONTRIBUTING.md`
- **enwp10 Database (wp10db)** (3 connections) — `README.md`
- **Production Rollback via Immutable Image Tags** (3 connections) — `README.md`
- **Dev Service: dev-web (Flask API on 5000)** (3 connections) — `docker-compose-dev.yml`
- **Codecov Coverage Configuration (90% project target)** (2 connections) — `.codecov.yml`
- **CI Job: black-format-check** (2 connections) — `.github/workflows/ci.yml`
- **Immutable Release Tags for Rollback** (2 connections) — `.github/workflows/publish.yml`
- **Pre-commit Hooks Configuration (whitespace, prettier, black)** (2 connections) — `.pre-commit-config.yaml`
- **WP1 Code Standards** (2 connections) — `CONTRIBUTING.md`
- **cron_config.py Recurring Jobs (RQ cron scheduler)** (2 connections) — `README.md`
- _... and 20 more nodes in this community_

## Relationships

- No strong cross-community connections detected

## Source Files

- `.codecov.yml`
- `.github/FUNDING.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/publish.yml`
- `.pre-commit-config.yaml`
- `.readthedocs.yaml`
- `CONTRIBUTING.md`
- `README.md`
- `db/README.md`
- `docker-compose-dev.yml`
- `docker-compose-test.yml`
- `docker-compose.yml`
- `docker/README.md`
- `docker/dev-db/README.md`
- `docker/dev-frontend/README.md`
- `docker/dev-workers/README.md`

## Audit Trail

- EXTRACTED: 90 (69%)
- INFERRED: 40 (31%)
- AMBIGUOUS: 0 (0%)

---

_Part of the graphify knowledge wiki. See [index](index.md) to navigate._
