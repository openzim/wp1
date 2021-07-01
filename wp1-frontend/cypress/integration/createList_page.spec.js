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

  it('unsucessful response', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('.needs-validation').then(form$ => {
      form$.on('submit', e => {
        e.preventDefault();
      });
    });
    cy.get('#listName > .form-control')
      .click()
      .type('List Name');
    cy.get('#items > .form-control')
      .click()
      .type('Eiffel_Tower\nStatue of Liberty#');
    cy.intercept('v1/selection/').as('selection');
    cy.get('#saveListButton').click();
    cy.wait('@selection');
    cy.get('#items > .form-control').should('have.value', 'Eiffel_Tower');
    cy.get('#invalid_articles').contains(
      'Following items are not valid for selection lists beacuse they have #'
    );
    cy.get('#invalid_articles > .form-control').should(
      'have.value',
      'Statue_of_Liberty#'
    );
  });

  it('successful response', () => {
    cy.visit('/#/selection/lists/simple/new');
    cy.get('.needs-validation').then(form$ => {
      form$.on('submit', e => {
        e.preventDefault();
      });
    });
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
