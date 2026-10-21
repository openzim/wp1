/// <reference types="Cypress" />

describe('the compare projects page', () => {
  beforeEach(() => {
    // ArticleTable renders paired rows (row[0]/row[1]) when projectIdB is
    // set, so the flat single-project fixture is reshaped into pairs here
    // rather than stubbed as-is.
    cy.fixture('articles_alien_predator.json').then((articles) => {
      cy.intercept('v1/projects/Alien/articles?projectB=Aesthetics*', {
        ...articles,
        articles: articles.articles.map((article) => [article, article]),
      }).as('compareArticles');
    });
  });

  describe('with no URL parameters', () => {
    beforeEach(() => {
      cy.visit('/#/compare');
    });

    it('successfully loads', () => {});

    it('shows two autocompletes and a disabled compare button', () => {
      cy.get('input.search').should('have.length', 2);
      cy.contains('button', 'Compare').should('have.attr', 'disabled');
    });

    it('enables compare after selecting two projects', () => {
      cy.get('input.search').eq(0).type('Alien');
      cy.get('.results:visible .result').first().click();
      cy.get('input.search').eq(1).type('Aesthetics');
      cy.get('.results:visible .result').first().click();
      cy.contains('button', 'Compare').should('not.have.attr', 'disabled');
    });

    it('navigates and renders the table on compare click', () => {
      cy.get('input.search').eq(0).type('Alien');
      cy.get('.results:visible .result').first().click();
      cy.get('input.search').eq(1).type('Aesthetics');
      cy.get('.results:visible .result').first().click();
      cy.contains('button', 'Compare').click();
      cy.url().should('include', '/#/compare/Alien/Aesthetics');
      cy.wait('@compareArticles');
      cy.contains('Alien vs. Predator (film)');
    });
  });

  describe('with projects in the URL', () => {
    beforeEach(() => {
      cy.visit('/#/compare/Alien/Aesthetics');
    });

    it('prefills both autocompletes', () => {
      cy.get('input.search').eq(0).should('have.value', 'Alien');
      cy.get('input.search').eq(1).should('have.value', 'Aesthetics');
    });

    it('renders the comparison table without a compare button', () => {
      cy.wait('@compareArticles');
      cy.contains('button', 'Compare').should('not.exist');
      cy.contains('Alien vs. Predator (film)');
    });

    it('labels quality and importance filter dropdowns for accessibility', () => {
      cy.get('label[for="project-a-quality"]').should('contain.text', 'Quality');
      cy.get('#project-a-quality').should(
        'have.attr',
        'aria-label',
        'Project A Quality'
      );
      cy.get('label[for="project-a-importance"]').should(
        'contain.text',
        'Importance'
      );
      cy.get('#project-a-importance').should(
        'have.attr',
        'aria-label',
        'Project A Importance'
      );

      cy.get('label[for="project-b-quality"]').should('contain.text', 'Quality');
      cy.get('#project-b-quality').should(
        'have.attr',
        'aria-label',
        'Project B Quality'
      );
      cy.get('label[for="project-b-importance"]').should(
        'contain.text',
        'Importance'
      );
      cy.get('#project-b-importance').should(
        'have.attr',
        'aria-label',
        'Project B Importance'
      );
    });
  });
});
