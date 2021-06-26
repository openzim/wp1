/// <reference types="Cypress" />

describe('the createList page', () => {
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

  it('list name validation', () => {
    cy.get('#saveListButton').click();
    cy.get('#listName').contains('Please provide a valid List Name.');
  });

  it('textbox item validation', () => {
    cy.get('#saveListButton').click();
    cy.get('#items').contains('Please provide valid items.');
  });

  it('list name validation on blur', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('#listName > .form-control').click();
    cy.get('#listName').contains('Please provide a valid List Name.');
  });

  it('textbox item validation on blur', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('#items > .form-control').click();
    cy.get('#items').contains('Please provide valid items.');
  });
});
