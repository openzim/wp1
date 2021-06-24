/// <reference types="Cypress" />

describe('the createList page', () => {
  it('successfully loads', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('nav').contains('Create Simple List');
  });

  it('displays wiki projects', () => {
    cy.get('select').select('ab.wikipedia.org');
  });

  it('displays List Name', () => {
    cy.get('#listName')
      .click()
      .type('My List');
  });

  it('displays textbox', () => {
    cy.get('textarea')
      .click()
      .type('Items');
    cy.get('#saveListButton').click();
  });
});
