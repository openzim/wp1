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

    // Don't continue until the table has been updated.
    cy.wait('@predatorArticles');
    cy.get('tr')
      .contains('Prometheus')
      .should('not.exist');

    cy.get('table')
      .find('tr')
      .each($el => {
        cy.wrap($el).should('contain.text', 'Predator');
      });
  });

  describe('custom pagination', () => {
    it('shows 50 rows in article-table', () => {
      cy.visit('/#/project/Alien/articles');
      cy.contains('Custom pagination').click();

      cy.get('input')
        .eq(0)
        .clear()
        .type('50');

      cy.get('input')
        .eq(1)
        .clear()
        .type('2');

      cy.get('button')
        .eq(1)
        .click();

      cy.get('tr')
        .eq(0)
        .find('td')
        .eq(0)
        .should('have.text', '51');

      cy.get('tr').should('have.length', 50);
    });
  });

  describe('Select Quality/Importance', () => {
    it('displays articles with selected quality and importance', () => {
        cy.visit('/#/project/Alien/articles');
        cy.intercept('v1/projects/Alien/articles?importance=Top-Class&quality=B-Class').as(
          'TopBArticles'
        );

        cy.contains('Select Quality/Importance')
          .click();
        
        cy.get('.custom-select')
        .eq(0)
        .select('B');

        cy.get('.custom-select')
        .eq(1)
        .select('Top');

        cy.get('button')
          .eq(2)
          .click();
        
        cy.wait('@TopBArticles');
        
        cy.get('tr')
        .contains('Prometheus')
        .should('not.exist');

        cy.get('table')
          .find('tr')
          .each($el => {
            cy.wrap($el).should('contain.text', 'Top');
            cy.wrap($el).should('contain.text', 'B');
          });
    });
  });
});
