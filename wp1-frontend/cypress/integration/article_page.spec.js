/// <reference types="Cypress" />

describe('the article page', () => {
  it('filters by article name', () => {
    cy.visit('/#/project/Alien/articles');
    cy.intercept('v1/projects/Alien/articles?articlePattern=Predator').as(
      'predatorArticles'
    );

    cy.contains('a', 'Filter by article name').click();

    cy.get('input')
      .eq(2)
      .type('Predator');
    cy.get('button')
      .eq(3)
      .click();

    cy.wait('@predatorArticles');

    cy.get('table')
      .find('tr')
      .each($el => {
        cy.wrap($el).should('contain.text', 'Predator');
      });
  });
});
