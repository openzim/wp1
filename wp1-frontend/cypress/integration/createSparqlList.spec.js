/// <reference types="Cypress" />

describe('the create SPARQL builder page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
      cy.visit('/#/selections/sparql');
    });

    it('successfully loads', () => {});

    it('displays wiki projects', () => {
      cy.get('select').contains('aa.wikipedia.org');
      cy.get('select').contains('en.wiktionary.org');
      cy.get('select').contains('en.wikipedia.org');
    });

    it('validates list name on clicking save', () => {
      cy.get('#saveListButton').click();
      cy.get('#listName').contains('Please provide a valid selection name');
    });

    it('validates textbox on clicking save', () => {
      cy.get('#saveListButton').click();
      cy.get('#listName > .invalid-feedback').should('be.visible');
      cy.get('#items > .invalid-feedback').should('be.visible');
    });

    it('validates list name on losing focus', () => {
      cy.get('#listName > .form-control').click();
      cy.get('#items > .form-control').click();
      cy.get('#listName > .invalid-feedback').should('be.visible');
    });

    it('validates textbox on losing focus', () => {
      cy.get('#items > .form-control').click();
      cy.get('#listName > .form-control').click();
      cy.get('#items > .invalid-feedback').should('be.visible');
    });

    it('redirects on saving valid builder', () => {
      cy.get('#listName > .form-control').click().type('List Name');
      cy.get('#items > .form-control').click().type('SELECT ?article FROM foo');
      cy.intercept('v1/builders/', { fixture: 'save_list_success.json' });
      cy.get('#saveListButton').click();
      cy.url().should('eq', 'http://localhost:3000/#/selections/user');
    });
  });

  describe('when the user is not logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
    });

    it('opens login page', () => {
      cy.visit('/#/selections/sparql');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
