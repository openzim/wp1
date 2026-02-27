const { defineConfig } = require('cypress');

module.exports = defineConfig({
  chromeWebSecurity: false,
  e2e: {
    setupNodeEvents(on, config) {
      return require('./cypress/plugins/index.js')(on, config);
    },
    baseUrl: 'http://localhost:5173',
    video: false,
  },
  component: {
    devServer: {
      framework: 'vue',
      bundler: 'vite',
    },
    specPattern: 'cypress/component/**/*.cy.{js,ts,jsx,tsx}', 
  },
});