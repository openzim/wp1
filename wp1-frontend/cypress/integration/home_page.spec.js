/// <reference types="Cypress" />

describe('the home page', () => {
  it('successfully loads', () => {
    cy.visit('/');
  });

  it('autocompletes for Water', () => {
    cy.visit('/');

    cy.get('.search').type('Water');

    cy.get('.results').should('be.visible');
    cy.get('.results')
      .children('li')
      .eq(1)
      .should('contain.text', 'Water');
  });

  it('project-table for Alien displayed', () => {
    cy.visit('/');

    cy.get('.search').type('Alien');

    cy.get('.results').should('be.visible');
    cy.get('.results')
      .children('li')
      .eq(0)
      .should('contain.text', 'Alien');
      
    cy.intercept('/v1/projects/Alien/table').as('table');
    cy.visit('/#/project/Alien');
    cy.wait('@table', {timeout: 15000});

    cy.get('table').should('be.visible')
      .eq(0)
      .should('contain.text','Alien articles by quality and importance')
  });
});