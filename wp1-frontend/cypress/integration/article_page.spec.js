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
        cy.get('table').find('tr').each(($el) => {
            cy.wrap($el).should('contain.text', 'Predator');
        });
    });
});

describe('custom pagination', () => {
    it('shows 50 rows in article-table', () => {
        cy.visit('/#/project/Alien/articles');
    
        cy.contains('Custom pagination').click();
        cy.get('input').eq(0).clear().type('50');
        cy.get('input').eq(1).clear().type('2');
        cy.get('button').eq(1).click();
    
        cy.get('tr').eq(0).find('td').eq(0).should('have.text', '51');
        cy.get('tr').should('have.length', 50);
    });
});
