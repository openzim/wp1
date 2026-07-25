// ***********************************************************
// This example support/index.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands';

// The replag banner script is third-party code fetched live from wmflabs on
// every page load. Upstream changes to it can throw in the test browser and
// fail every spec (Cypress fails tests on any uncaught exception). No test
// asserts on the banner, so serve an empty script instead.
beforeEach(() => {
  cy.intercept(
    { url: 'https://tools-static.wmflabs.org/replag-embed/replag-embed.js' },
    { body: '' }
  );
});

// Default stubs for API endpoints that components fetch on nearly every
// page, so that no test depends on the Python backend being up. The
// responses mirror what the real backend returns when there is no login
// session (the state CI used to run in). Specs override these with their
// own cy.intercept calls where a test needs different data — intercepts
// defined later (i.e. in the spec) take precedence over these.
beforeEach(() => {
  cy.intercept('v1/oauth/identify', { statusCode: 401, body: 'Unauthorized' });
  cy.intercept('v1/oauth/email', { statusCode: 401, body: 'Unauthorized' });
  cy.intercept('v1/selection/simple/lists', {
    statusCode: 401,
    body: 'Unauthorized',
  });
  cy.intercept('v1/builders/*', { statusCode: 401, body: 'Unauthorized' });
  cy.intercept('v1/sites/', { fixture: 'sites.json' });
  cy.intercept('v1/projects/count', { fixture: 'projects_count.json' });
  cy.intercept('v1/projects/', { fixture: 'projects.json' });
  cy.intercept('v1/projects/*/category_links', {
    fixture: 'category_links_alien.json',
  });
  cy.intercept('v1/projects/*/category_links/sorted', {
    fixture: 'category_links_sorted_alien.json',
  });
});

// Alternatively you can use CommonJS syntax:
// require('./commands')
