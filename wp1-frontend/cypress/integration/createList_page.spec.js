/// <reference types="Cypress" />

describe('the CreateSimpleList page', () => {
  beforeEach(() => {
    cy.intercept('v1/sites/', { fixture: 'sites.json' });
  });

  it('successfully loads', () => {
    cy.visit('/#/selection/lists/simple/new');
  });

  it('displays wiki projects', () => {
    cy.get('select').contains('aa.wikipedia.org');
    cy.get('select').contains('en.wiktionary.org');
    cy.get('select').contains('en.wikipedia.org');
  });

  it('validates list name on clicking save', () => {
    cy.get('#saveListButton').click();
    cy.get('#listName').contains('Please provide a valid List Name.');
  });

  it('validates textbox on clicking save', () => {
    cy.get('#saveListButton').click();
    cy.get('#items').contains('Please provide valid items.');
  });

  it('validates list name on losing focus', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('#listName > .form-control').click();
    cy.get('#listName').contains('Please provide a valid List Name.');
  });

  it('validates textbox on losing focus', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('#items > .form-control').click();
    cy.get('#items').contains('Please provide valid items.');
  });

  it('displays a textbox with invalid article names', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('#listName > .form-control')
      .click()
      .type('List Name');
    cy.get('#items > .form-control')
      .click()
      .type('Eiffel_Tower\nStatue of#Liberty');
    cy.intercept('v1/selection/').as('selection');
    cy.get('#saveListButton').click();
    cy.wait('@selection');
    cy.get('#items > .form-control').should('have.value', 'Eiffel_Tower');
    cy.get('#invalid_articles').contains(
      'Following items are not valid for selection lists because they have #'
    );
    cy.get('#invalid_articles > .form-control').should(
      'have.value',
      'Statue_of#Liberty'
    );
  });

  it('redirects on saving valid article names', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('#listName > .form-control')
      .click()
      .type('List Name');
    cy.get('#items > .form-control')
      .click()
      .type('Eiffel_Tower\nStatue of Liberty');
    cy.intercept('v1/selection/').as('selection');
    cy.get('#saveListButton').click();
    cy.wait('@selection');
    cy.url().should('eq', 'http://localhost:3000/#/selection/user');
  });
});
