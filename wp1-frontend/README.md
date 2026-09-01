# wp1-frontend

The frontend for the WP 1.0 server: a [Vue 3](https://vuejs.org/)
single-page app (Options API) built with [Vite](https://vite.dev/).

## Styling: Tailwind

The whole app is styled with TailwindCSS; Bootstrap, jQuery and DataTables
were retired with the non-Selections redesign.

- Design tokens live in `tailwind.config.js` (from the OpenZIM Selections
  redesign handoff); shared component classes (`wp1r-btn-*`, `wp1r-input`,
  `wp1r-microlabel`, …) live in `src/tailwind.css` under a `.wp1r` wrapper
  class that the page shells and the app chrome apply.
- The assessment tables (project matrix, article list rating cells, compare
  table) intentionally keep the canonical Wikipedia wikitable identity: the
  `.wt`/`.wt-head`/`.wt-gap` classes in `src/tailwind.css` plus the
  full-cell class fills in `src/labels.css`.

## Project setup

In the docker-compose dev environment, the frontend runs in its own container
with hot reload (see [docker/dev-frontend](../docker/dev-frontend/README.md))
and nothing needs to be installed locally. To run it outside Docker instead,
you need [Node.js](https://nodejs.org/) version 22 and pnpm (if you don't
have pnpm, enable it with `corepack enable`), then:

    pnpm install

### Development server (hot reload, port 5173)

    pnpm dev

### Production build

    pnpm build

### Preview the production build (port 5173)

    pnpm serve

## End-to-end tests

The Cypress suite is hermetic — every API call is stubbed with
`cy.intercept`, so no backend is needed. With the dev server (or a
built bundle served on port 5173) running:

    pnpm exec cypress run

or interactively:

    pnpm exec cypress open
