/// <reference types="Cypress" />

describe('the article page', () => {
  beforeEach(() => {
    cy.intercept('v1/projects/Alien', { fixture: 'project_alien.json' });
    cy.intercept('v1/projects/Alien/articles', {
      fixture: 'articles_alien.json',
    });
  });

  it('filters by article name', () => {
    cy.visit('/#/project/Alien/articles');
    cy.intercept('v1/projects/Alien/articles?articlePattern=Predator', {
      fixture: 'articles_alien_predator.json',
    }).as('predatorArticles');

    cy.get('#updateName').type('Predator');
    cy.get('#updateRating').click();

    // Don't continue until the table has been updated.
    cy.wait('@predatorArticles');
    cy.get('tr').contains('Prometheus').should('not.exist');

    cy.get('table')
      .find('tbody tr')
      .each(($el) => {
        cy.wrap($el).should('contain.text', 'Predator');
      });
  });

  it('commits the name filter on Enter', () => {
    cy.visit('/#/project/Alien/articles');
    cy.intercept('v1/projects/Alien/articles?articlePattern=Predator', {
      fixture: 'articles_alien_predator.json',
    }).as('predatorArticles');

    cy.get('#updateName').type('Predator{enter}');

    cy.wait('@predatorArticles');
    cy.get('tr').contains('Prometheus').should('not.exist');
  });

  it('links to a TSV download of the full filtered list', () => {
    cy.visit('/#/project/Alien/articles');
    cy.intercept('v1/projects/Alien/articles?quality=B-Class', {
      fixture: 'articles_alien_top_b.json',
    }).as('BArticles');

    cy.get('#qualitySelect').select('B');
    cy.get('#updateRating').click();
    cy.wait('@BArticles');

    cy.contains('a', 'Download all results as TSV')
      .should('have.attr', 'href')
      .and(
        'match',
        /\/v1\/projects\/Alien\/articles\?quality=B-Class&format=tsv$/
      );
  });

  it('displays article on wikipedia', () => {
    // Serve a minimal stand-in for the Wikipedia article page, echoing the
    // requested title, so the test doesn't depend on wikipedia.org.
    cy.intercept('https://en.wikipedia.org/w/index.php*', (req) => {
      const title = new URL(req.url).searchParams.get('title');
      req.reply(
        `<html><body><h1 id="firstHeading">${title}</h1></body></html>`
      );
    });

    cy.visit('/#/project/Alien/articles');

    cy.get('tbody tr')
      .eq(0)
      .find('td')
      .find('a')
      .eq(0)
      .invoke('text')
      .then(($text) => {
        cy.get('tbody tr').eq(0).find('td').find('a').eq(0).click();
        cy.get('#firstHeading').should('contain.text', $text);
      });
  });

  describe('custom pagination', () => {
    it('shows 50 rows in article-table', () => {
      cy.visit('/#/project/Alien/articles');
      cy.intercept('/v1/projects/Alien/articles?page=2&numRows=50', {
        fixture: 'articles_alien_page2.json',
      }).as('Pagination');

      cy.get('#row-input').clear().type('50');

      cy.get('#page-input').clear().type('2');

      cy.get('#updateRating').click();

      cy.wait('@Pagination');
      cy.get('tr').contains('Prometheus').should('not.exist');

      cy.get('tbody tr').eq(0).find('td').eq(0).should('have.text', '51');

      cy.get('tbody tr').should('have.length', 50);
    });

    it('blocks the commit on invalid pagination values', () => {
      cy.visit('/#/project/Alien/articles');

      cy.get('#row-input').clear().type('9999');
      cy.get('#updateRating').click();

      cy.url().should('not.include', 'numRows=9999');
    });
  });

  describe('Select Quality/Importance', () => {
    it('displays articles with selected quality and importance', () => {
      cy.visit('/#/project/Alien/articles');
      cy.intercept(
        'v1/projects/Alien/articles?importance=Top-Class&quality=B-Class',
        { fixture: 'articles_alien_top_b.json' }
      ).as('TopBArticles');

      cy.get('#qualitySelect').select('B');

      cy.get('#importanceSelect').select('Top');

      cy.get('#updateRating').click();

      cy.wait('@TopBArticles');

      cy.get('tr').contains('Prometheus').should('not.exist');

      cy.get('table')
        .find('tbody tr')
        .each(($el) => {
          cy.wrap($el).should('contain.text', 'Top');
          cy.wrap($el).should('contain.text', 'B');
        });
    });

    it('opens a random article with selected quality and importance', () => {
      cy.visit('/#/project/Alien/articles');

      cy.intercept(
        'GET',
        'v1/projects/Alien/articles/random?quality=B-Class&importance=Top-Class',
        {
          statusCode: 200,
          body: JSON.stringify(
            'https://en.wikipedia.org/w/index.php?title=Predator%20%28film%29'
          ),
        }
      ).as('RandomTopBArticle');

      cy.window().then((win) => {
        cy.stub(win, 'open').as('windowOpen');
      });

      cy.get('#qualitySelect').select('B');

      cy.get('#importanceSelect').select('Top');

      cy.get('#randomArticle').click();

      cy.wait('@RandomTopBArticle').then((interception) => {
        const randomArticleLink = JSON.parse(interception.response.body);

        cy.get('@windowOpen').should('be.calledWith', randomArticleLink);
      });
    });
  });
});
