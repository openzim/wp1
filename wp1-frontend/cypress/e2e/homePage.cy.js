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
});
