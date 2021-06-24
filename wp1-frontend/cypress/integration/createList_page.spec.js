/// <reference types="Cypress" />

describe('the createList page', () => {
  it('successfully loads', () => {
    cy.intercept('v1/sites/', { fixture: 'sites.json' });
    cy.visit('/#/selection/lists/simple/new');
  });

  it('displays wiki projects', () => {
    cy.get('select').contains('aa.wikipedia.org');
    cy.get('select').contains('en.wiktionary.org');
    cy.get('select').contains('en.wikipedia.org');
  });

  it('displays list name', () => {
    cy.get('#saveListButton').click();
    cy.on('window:alert', txt => {
      expect(txt).to.contains('Please fill in this field');
    });
    cy.get('#listName')
      .click()
      .type('My List');
  });

  it('displays textbox', () => {
    cy.get('#saveListButton').click();
    cy.on('window:alert', txt => {
      expect(txt).to.contains('Please fill in this field');
    });
  });
});
