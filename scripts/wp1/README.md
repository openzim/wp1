# Production scripts

This directory holds the scripts that deploy and operate the production WP1
instance, which runs on a Wikimedia Cloud VPS box.

## Updating production

Deploys are done with `deploy.sh`, run from a local checkout:

```bash
./scripts/wp1/deploy.sh
```

This deploys the current `origin/main`. It requires push access to this
repository and ssh access (with sudo) to the production box,
`mwcurator-b.mwoffliner.eqiad1.wikimedia.cloud` (override with the
`WP1_DEPLOY_HOST` environment variable; see
[SSH access](#ssh-access-to-the-production-box) below for one-time
setup). The script:

- Pushes `origin/main` to the `release` branch (a plain, non-forced
  push: if `release` has diverged from `main` the push is rejected and
  a human needs to sort it out). This triggers the
  [publish workflow](https://github.com/openzim/wp1/actions/workflows/publish.yml),
  which builds and pushes the `wp1-workers`, `wp1-web` and
  `wp1-frontend` docker images.
- Runs `deploy-remote.sh` on the production box (after a
  `git pull` there, so the remote script is the version being
  deployed), which:
  - Warns and asks for confirmation if `.env.example` changed since the
    last deploy, since the production env file `/data/wp1bot/wp1.env`
    (consumed by `docker-compose.yml` via `env_file`) is managed by hand
    and probably needs a matching update.
  - Waits for all three images tagged `sha-<short sha>` for the exact
    commit being deployed to appear on ghcr.io. Deploying by the
    immutable sha tag (instead of pulling the moving `release` tag)
    guarantees a consistent image set; the three build jobs finish at
    different times, so `release` can briefly point at a mixed set.
  - Pulls the three images, re-tags them locally as `release` (the tag
    `docker-compose.yml` uses), and runs `docker compose up -d`. Only
    those three images are ever pulled -- never `docker compose pull`,
    which would also refresh infrastructure images like the pinned
    redis (see [Redis persistence](#redis-persistence) below).
  - Applies database migrations:
    `yoyo -c /usr/src/app/db/production/yoyo.ini apply --batch` in the
    workers container.
  - Verifies that the containers are running and that
    https://api.wp1.openzim.org and https://wp1.openzim.org respond.

`deploy-remote.sh` can also be run by hand on the box
(`cd /data/code/wp1 && sudo ./scripts/wp1/deploy-remote.sh <full git sha>`)
if the local half already pushed `release` but the remote half failed
or was interrupted; it is safe to re-run.

## Rolling back production

In addition to the moving `release` tag, every push to the `release`
branch publishes each image with two immutable tags: `release-<n>`
(where `<n>` is the run number of the publish workflow) and
`sha-<git sha>`. The available versions for each image are listed on
its GitHub packages page:

- https://github.com/openzim/wp1/pkgs/container/wp1-workers/versions
- https://github.com/openzim/wp1/pkgs/container/wp1-web/versions
- https://github.com/openzim/wp1/pkgs/container/wp1-frontend/versions

To roll back a bad deploy, run (from a local checkout):

```bash
./scripts/wp1/deploy.sh --rollback release-141   # or e.g. sha-73ed612
```

This runs `deploy-remote.sh --rollback <tag>` on the box, which
pulls that version of each image, re-tags it locally as `release` (no
registry login or push is required, the local tag is what docker
compose uses), and recreates the containers. A successful deploy prints
the sha tag of the version it replaced, which is the tag to pass here.

Note that the next normal deploy rolls forward again. Rolling back
database migrations is deliberately not automated; if the deploy being
rolled back included migrations, roll those back by hand on the box:

- `sudo docker exec -ti -e PYTHONPATH=. wp1bot-workers yoyo -c /usr/src/app/db/production/yoyo.ini rollback`

## SSH access to the production box

The production box is a [Wikimedia Cloud VPS](https://wikitech.wikimedia.org/wiki/Portal:Cloud_VPS)
instance in the `mwoffliner` project. It is not reachable directly from
the internet; ssh goes through the Cloud VPS bastion. One-time setup
(see [Help:Accessing Cloud VPS instances](https://wikitech.wikimedia.org/wiki/Help:Accessing_Cloud_VPS_instances)
for the full guide):

1. [Create a Wikimedia developer account](https://idm.wikimedia.org/signup/)
   and [upload your public SSH key](https://idm.wikimedia.org/keymanagement/).
2. Ask an existing member to add you to the `mwoffliner` Cloud VPS project.
3. Add the bastion jump host to your `~/.ssh/config` (use your _shell_
   username from idm.wikimedia.org, which may differ from your account
   username):

   ```
   Host *.wikimedia.cloud
     User <your-shell-name>
     ProxyJump bastion.wmcloud.org:22
   ```

Then `ssh mwcurator-b.mwoffliner.eqiad1.wikimedia.cloud` should log you
in without a password, which is what `deploy.sh` needs.

## Redis persistence

Redis holds the RQ queue state and the only copy of the rolling 7-day
article assessment log history (used to generate the on-wiki log pages).
The `redis` service therefore stores its data in the `redis-data` volume
and its image tag is pinned in `docker-compose.yml`. To upgrade Redis,
bump the tag deliberately and deploy normally; the volume preserves the
data across the container recreation. Do not deploy with an unpinned
`redis` image: a surprise upstream image update recreates the container,
and before the volume existed that meant losing the entire keyspace
(this happened on 2026-08-01 and overwrote hundreds of on-wiki log pages
with false "no logs" notices; see
[issue #1244](https://github.com/openzim/wp1/issues/1244)).

## Operational one-offs

The Python scripts in this directory are small operational tools, run inside a
container (their config defaults point at in-docker hostnames; each script's
header comment shows the exact invocation):

- `enqueue-project.py` — enqueue an update job for a single project.
- `warm-assessment-cache.py` — enqueue the assessment cache warming job.
- `clear-project-table-caches.py` — clear the cached per-project tables.
