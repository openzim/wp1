# Development Frontend Docker Image

This Dockerfile creates a development environment for the Vue.js frontend with
hot-reload support. It is used by `docker-compose-dev.yml` to run the frontend
without requiring Node.js to be installed locally.

## features

- Hot-reload support via Vite dev server
- Source files are mounted as volumes for live editing
- No local Node.js installation required

## usage

The dev-frontend container is started automatically as part of the dev stack:

```bash
docker compose -f docker-compose-dev.yml up --build
```

The frontend will be available at http://localhost:5173.

## Volume Mounts

The following files/directories are mounted from the host:

- `wp1-frontend/src/` - Vue component source files
- `wp1-frontend/index.html` - Entry HTML file
- `wp1-frontend/vite.config.js` - Vite configuration
- `wp1-frontend/postcss.config.js` - PostCSS configuration

Changes to these files will be automatically detected and the browser will
refresh accordingly.
