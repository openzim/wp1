/// <reference types="Cypress" />

describe('the article page', () => {
    it('filters by article name', () => {
        cy.visit('/#/project/Alien/articles');
        
        cy.contains('a', 'Filter by article name').click();

        cy.get('input').eq(2).type('Predator');
        cy.get('button').eq(3).click();

        cy.get('table').find('tr').each(($el) => {
            cy.wrap($el).should('contain.text', 'Predator');
        });
    });
});