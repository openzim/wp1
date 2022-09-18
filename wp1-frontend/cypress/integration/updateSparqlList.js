/// <reference types="Cypress" />

describe('the update SPARQL list page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
    });

    describe('and the builder is found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          fixture: 'sparql_builder.json',
        });
        cy.visit('/#/selections/sparql/1');
      });

      it('successfully loads', () => {});

      it('displays wiki projects', () => {
        cy.get('select').contains('aa.wikipedia.org');
        cy.get('select').contains('en.wiktionary.org');
        cy.get('select').contains('en.wikipedia.org');
      });

      it('displays builder information', () => {
        cy.get('#listName > .form-control').should('have.value', 'Builder 2');
        cy.get('#items > .form-control').should(
          'have.value',
          'SELECT ?foo FROM bar'
        );
        cy.get('#project > select').should('have.value', 'en.wiktionary.org');
      });

      it('does not show invalid list items', () => {
        cy.get('#updateListButton').click();
        cy.get('#items > .invalid-feedback').should('not.be.visible');
      });

      it('does not show invalid list name', () => {
        cy.get('#updateListButton').click();
        cy.get('#listName > .invalid-feedback').should('not.be.visible');
      });

      it('redirects on saving valid article names', () => {
        cy.intercept('v1/builders/1', { fixture: 'save_list_success.json' });
        cy.get('#updateListButton').click();
        cy.url().should('eq', 'http://localhost:3000/#/selections/user');
      });
    });

    describe('and the builder is not found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          statusCode: 404,
          body: '404 NOT FOUND',
        });
        cy.visit('/#/selections/sparql/1');
      });

      it('displays the 404 text', () => {
        cy.get('#404').should('be.visible');
      });
    });
  });

  describe('when the user is not logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
    });

    it('opens login page', () => {
      cy.visit('/#/selections/sparql/1');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
