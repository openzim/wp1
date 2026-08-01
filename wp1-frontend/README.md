# wp1-frontend

The frontend for the WP 1.0 server: a [Vue 3](https://vuejs.org/)
single-page app (Options API) built with [Vite](https://vite.dev/).

## Project setup

    yarn install

### Development server (hot reload, port 5173)

    yarn dev

### Production build

    yarn build

### Preview the production build (port 5173)

    yarn serve

## End-to-end tests

The Cypress suite is hermetic — every API call is stubbed with
`cy.intercept`, so no backend is needed. With the dev server (or a
built bundle served on port 5173) running:

    $(yarn bin)/cypress run

or interactively:

    $(yarn bin)/cypress open
