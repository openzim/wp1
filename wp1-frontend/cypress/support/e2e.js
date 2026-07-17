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

// Alternatively you can use CommonJS syntax:
// require('./commands')
