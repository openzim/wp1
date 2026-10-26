/// <reference types="Cypress" />

describe('the home page', () => {
  beforeEach(() => {
    cy.intercept('v1/projects/count', { body: { count: 2187 } });
    cy.intercept('v1/projects/Alien/table', {
      fixture: 'project_table_alien.json',
    });
  });

  it('successfully loads', () => {
    cy.visit('/');
    cy.contains('h2', 'Projects');
    cy.contains('2,187 projects tracked');
  });

  it('autocompletes for Water', () => {
    cy.visit('/');

    cy.get('.search').type('Water');

    cy.get('.results').should('be.visible');
    cy.get('.results').children('li').eq(1).should('contain.text', 'Water');
  });

  it('project-table for Alien displayed', () => {
    cy.visit('/');

    cy.get('.search').type('Alien');

    cy.get('.results').should('be.visible');
    cy.get('.results')
      .children('li')
      .eq(0)
      .should('contain.text', 'Alien')
      .click();

    cy.contains('h2', 'Alien');
    cy.get('table')
      .should('be.visible')
      .should('contain.text', 'Quality')
      .should('contain.text', 'Importance');
    cy.contains('Last updated');
  });

  it('has meta color-scheme configured for light and dark', () => {
    cy.visit('/');
    cy.document().then((doc) => {
      const meta = doc.querySelector('meta[name="color-scheme"]');
      expect(meta).to.exist;
      expect(meta.getAttribute('content')).to.contain('dark');
    });
  });

  describe('color scheme preference emulation', { browser: { family: 'chromium' } }, () => {
    const setColorScheme = (scheme) => {
      return cy.wrap(
        Cypress.automation('remote:debugger:protocol', {
          command: 'Emulation.setEmulatedMedia',
          params: {
            features: scheme ? [{ name: 'prefers-color-scheme', value: scheme }] : [],
          },
        })
      );
    };

    afterEach(() => {
      setColorScheme(null);
    });

    it('renders light mode variables when prefers-color-scheme is light', () => {
      setColorScheme('light');
      cy.visit('/');
      cy.document().then((doc) => {
        const style = doc.defaultView.getComputedStyle(doc.documentElement);
        expect(style.getPropertyValue('--color-page').trim()).to.equal('#eceeef');
        expect(style.getPropertyValue('--color-surface').trim()).to.equal('#ffffff');
        expect(style.getPropertyValue('--color-ink').trim()).to.equal('#14171a');
      });
    });

    it('renders dark mode variables when prefers-color-scheme is dark', () => {
      setColorScheme('dark');
      cy.visit('/');
      cy.document().then((doc) => {
        const style = doc.defaultView.getComputedStyle(doc.documentElement);
        expect(style.getPropertyValue('--color-page').trim()).to.equal('#101418');
        expect(style.getPropertyValue('--color-surface').trim()).to.equal('#1c2128');
        expect(style.getPropertyValue('--color-ink').trim()).to.equal('#f0f3f6');
      });
    });
  });
});
