/// <reference types="Cypress" />

describe('when the user is logged in', () => {
  beforeEach(() => {
    cy.intercept('v1/sites/', { fixture: 'sites.json' });
    cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
    cy.visit('/#/selections/simple');
  });

  it('successfully loads', () => {});

  it('displays wiki projects', () => {
    cy.get('select').contains('aa.wikipedia.org');
    cy.get('select').contains('en.wiktionary.org');
    cy.get('select').contains('en.wikipedia.org');
  });

  it('validates list name on clicking save', () => {
    cy.get('#saveListButton').click();
    cy.get('#listName').contains('Please provide a valid list name');
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

  it('displays a textbox with invalid article names', () => {
    cy.get('#listName > .form-control')
      .click()
      .type('List Name');
    cy.get('#items > .form-control')
      .click()
      .type('Eiffel_Tower\nStatue of#Liberty');
    cy.intercept('v1/builders/', { fixture: 'save_list_failure.json' });
    cy.get('#saveListButton').click();

    cy.get('#items > .invalid-feedback').should('not.be.visible');
    cy.get('#listName > .invalid-feedback').should('not.be.visible');

    cy.get('#items > .form-control').should('have.value', 'Eiffel_Tower');
    cy.get('#invalid_articles').contains(
      'The list contained the following invalid characters: #'
    );
    cy.get('#invalid_articles > .form-control').should(
      'have.value',
      'Statue_of#Liberty'
    );
  });

  it('redirects on saving valid article names', () => {
    cy.get('#listName > .form-control')
      .click()
      .type('List Name');
    cy.get('#items > .form-control')
      .click()
      .type('Eiffel_Tower\nStatue of Liberty');
    cy.intercept('v1/builders/', { fixture: 'save_list_success.json' });
    cy.get('#saveListButton').click();
    cy.url().should('eq', 'http://localhost:3000/#/selections/user');
  });
}),
  describe('when the user is not logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
    });

    it('opens login page', () => {
      cy.visit('/#/selections/simple');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
