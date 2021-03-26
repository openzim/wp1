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
      .should('contain.text', 'Alien')
      .click();

    cy.get('table').should('be.visible')
      .should('contain.text','Alien articles by quality and importance');
  });
});
  it('custom pagination works', () => {
    cy.visit('/#/project/Alien/articles');

    cy.contains('Custom pagination').click();
    cy.get('input').eq(0).clear().type('50');
    cy.get('input').eq(1).clear().type('2');
    cy.get('button').eq(1).click();

    cy.get('tr').eq(0).find('td').eq(0).should('have.text', '51');
    cy.get('tr').should('have.length', 50);
  });
});
