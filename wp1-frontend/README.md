# wp1-frontend

The frontend for the WP 1.0 server: a [Vue 3](https://vuejs.org/)
single-page app (Options API) built with [Vite](https://vite.dev/).

## Styling: Tailwind + Bootstrap (transitional)

The frontend is mid-migration from Bootstrap 4 to TailwindCSS:

- The redesigned **Selections** screens (`src/components/selections/`) and the
  global top navigation use Tailwind, configured in `tailwind.config.js` with
  the design tokens from the OpenZIM Selections redesign. Tailwind's preflight
  is disabled so it can't restyle the legacy pages; Tailwind-styled markup is
  scoped under a `.wp1r` wrapper class (see `src/tailwind.css`).
- All other pages (projects, articles, compare, update) are still Bootstrap 4
  and should stay that way until they are redesigned.
- New/redesigned pages should use Tailwind; don't mix the two systems within
  one component.

## Project setup

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
