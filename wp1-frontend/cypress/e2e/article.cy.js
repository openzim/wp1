/// <reference types="Cypress" />

describe('the article page', () => {
  it('filters by article name', () => {
    cy.visit('/#/project/Alien/articles');
    cy.intercept('v1/projects/Alien/articles?articlePattern=Predator').as(
      'predatorArticles'
    );

    cy.contains('a', 'Filter by article name').click();

    cy.get('input').eq(2).type('Predator');
    cy.get('#updateName').click();

    // Don't continue until the table has been updated.
    cy.wait('@predatorArticles');
    cy.get('tr').contains('Prometheus').should('not.exist');

    cy.get('table')
      .find('tr')
      .each(($el) => {
        cy.wrap($el).should('contain.text', 'Predator');
      });
  });

  it('displays article on wikipedia', () => {
    cy.visit('/#/project/Alien/articles');

    cy.get('tr')
      .eq(0)
      .find('td')
      .find('a')
      .eq(0)
      .invoke('text')
      .then(($text) => {
        cy.get('tr').eq(0).find('td').find('a').eq(0).click();
        cy.get('#firstHeading').should('contain.text', $text);
      });
  });

  describe('custom pagination', () => {
    it('shows 50 rows in article-table', () => {
      cy.visit('/#/project/Alien/articles');
      cy.intercept('/v1/projects/Alien/articles?page=2&numRows=50').as(
        'Pagination'
      );

      cy.contains('Custom pagination').click();

      cy.get('input').eq(0).clear().type('50');

      cy.get('input').eq(1).clear().type('2');

      cy.get('#updatePagination').click();

      cy.wait('@Pagination');
      cy.get('tr').contains('Prometheus').should('not.exist');

      cy.get('tr').eq(0).find('td').eq(0).should('have.text', '51');

      cy.get('tr').should('have.length', 50);
    });
  });

  describe('Select Quality/Importance', () => {
    let articleLinks = [];

    it('displays articles with selected quality and importance', () => {
      cy.visit('/#/project/Alien/articles');
      cy.intercept(
        'v1/projects/Alien/articles?importance=Top-Class&quality=B-Class'
      ).as('TopBArticles');

      cy.contains('Select Quality/Importance').click();

      cy.get('.custom-select').eq(0).select('B');

      cy.get('.custom-select').eq(1).select('Top');

      cy.get('#updateRating').click();

      cy.wait('@TopBArticles');

      cy.get('tr').contains('Prometheus').should('not.exist');

      cy.get('table')
        .find('tr')
        .each(($el) => {
          cy.wrap($el).should('contain.text', 'Top');
          cy.wrap($el).should('contain.text', 'B');
          const link = $el.find('td').eq(1).find('a').eq(0).attr('href');
          if (link) {
            articleLinks.push(link);
          }
        });
    });

    it('opens a random article with selected quality and importance', () => {
      cy.visit('/#/project/Alien/articles');
      cy.intercept(
        'v1/projects/Alien/articles/random?quality=B-Class&importance=Top-Class'
      ).as('RandomTopBArticle');

      cy.window().then((win) => {
        cy.stub(win, 'open').as('windowOpen');
      });

      cy.contains('Select Quality/Importance').click();

      cy.get('.custom-select').eq(0).select('B');

      cy.get('.custom-select').eq(1).select('Top');

      cy.get('#randomArticle').click();

      cy.wait('@RandomTopBArticle').then((interception) => {
        const randomArticleLink = interception.response.body;

        expect(articleLinks).to.include(randomArticleLink);

        cy.get('@windowOpen').should('be.calledWith', randomArticleLink);
      });
    });
  });
});
