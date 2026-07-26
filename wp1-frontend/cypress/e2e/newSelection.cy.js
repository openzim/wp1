/// <reference types="Cypress" />

describe('the new selection page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'login'
      );
      cy.visit('/#/selections/new');
      cy.wait('@login');
    });

    it('successfully loads with the simple source selected', () => {
      cy.contains('h1', 'New simple selection');
      cy.get('#articles').should('be.visible');
    });

    it('displays wiki projects in the project select', () => {
      cy.get('#project-select').contains('aa.wikipedia.org');
      cy.get('#project-select').contains('en.wiktionary.org');
      cy.get('#project-select').contains('en.wikipedia.org');
    });

    it('shows all six sources in the picker', () => {
      ['Simple', 'SPARQL', 'Petscan', 'Book', 'WikiProject', 'Combinator'].map(
        (label) => cy.contains('button', label)
      );
    });

    it('counts titles as they are typed', () => {
      cy.contains('0 titles detected');
      cy.get('#articles').type('Eiffel_Tower\nStatue_of_Liberty\n\n# comment');
      cy.contains('2 titles detected');
    });

    it('validates the name before saving', () => {
      cy.get('#articles').type('Eiffel_Tower');
      cy.get('#saveListButton').click();
      cy.contains('Please provide a selection name.');
    });

    it('validates the articles before saving', () => {
      cy.get('#name-input').type('List Name');
      cy.get('#saveListButton').click();
      cy.contains('Please provide at least one article title.');
    });

    it('keeps project and name when switching sources', () => {
      cy.get('#name-input').type('My List');
      cy.get('#project-select').select('en.wiktionary.org');
      cy.get('#source-sparql').click();
      cy.contains('h1', 'New SPARQL selection');
      cy.get('#name-input').should('have.value', 'My List');
      cy.get('#project-select').should('have.value', 'en.wiktionary.org');
      cy.url().should('include', 'source=sparql');
    });

    it('hands off to the combinator builder', () => {
      cy.get('#source-combinator').click();
      cy.url().should('include', '/selections/combinator');
    });

    it('displays a textbox with invalid article names on failure', () => {
      cy.get('#name-input').type('List Name');
      cy.get('#articles').type('Eiffel_Tower\nStatue of#Liberty');
      cy.intercept('POST', 'v1/builders/', {
        fixture: 'save_list_failure.json',
      }).as('save');
      cy.get('#saveListButton').click();
      cy.wait('@save');
      cy.get('#invalid_articles').contains(
        'The list contained the following invalid characters: #'
      );
      cy.get('#invalid_articles textarea').should(
        'have.value',
        'Statue_of#Liberty'
      );
      // The user's input is preserved so it can be fixed.
      cy.get('#articles').should(
        'have.value',
        'Eiffel_Tower\nStatue of#Liberty'
      );
    });

    it('disables the save button while saving', () => {
      cy.intercept('POST', 'v1/builders/', {
        delay: 2000,
        statusCode: 200,
        body: { success: true, id: 'new-id-1', items: {} },
      });
      cy.get('#name-input').type('List Name');
      cy.get('#articles').type('Eiffel_Tower');
      cy.get('#saveListButton').click();
      cy.get('#saveListButton').should('have.attr', 'disabled');
      cy.contains('Saving…');
    });

    it('redirects to the new selection detail on save', () => {
      cy.intercept('POST', 'v1/builders/', (req) => {
        expect(req.body.model).to.equal('wp1.selection.models.simple');
        expect(req.body.params.list).to.deep.equal([
          'Eiffel_Tower',
          'Statue of Liberty',
        ]);
        req.reply({
          statusCode: 200,
          body: { success: true, id: 'new-id-1', items: {} },
        });
      }).as('save');
      cy.get('#name-input').type('List Name');
      cy.get('#articles').type('Eiffel_Tower\nStatue of Liberty');
      cy.get('#saveListButton').click();
      cy.wait('@save');
      cy.url().should('include', '/selections/user/new-id-1');
    });

    describe('the SPARQL source', () => {
      beforeEach(() => {
        cy.get('#source-sparql').click();
      });

      it('shows the query field and saves a query', () => {
        cy.intercept('POST', 'v1/builders/', (req) => {
          expect(req.body.model).to.equal('wp1.selection.models.sparql');
          expect(req.body.params.query).to.contain('SELECT');
          req.reply({
            statusCode: 200,
            body: { success: true, id: 'new-id-2', items: {} },
          });
        }).as('save');
        cy.get('#name-input').type('Query List');
        cy.get('#query').type('SELECT ?article WHERE {}', {
          parseSpecialCharSequences: false,
        });
        cy.get('#saveListButton').click();
        cy.wait('@save');
        cy.url().should('include', '/selections/user/new-id-2');
      });

      it('imports a query from a Wikidata Query URL', () => {
        cy.get('#toggleUpdateQuery').click();
        cy.get('#updateQueryInput').type(
          'https://query.wikidata.org/#SELECT%20%3Fitem',
          { parseSpecialCharSequences: false }
        );
        cy.get('#updateQuery').click();
        cy.get('#query').should('have.value', 'SELECT ?item');
      });

      it('shows an error for a non-Wikidata URL', () => {
        cy.get('#toggleUpdateQuery').click();
        cy.get('#updateQueryInput').type('https://example.com/#foo');
        cy.get('#updateQuery').click();
        cy.contains('Could not extract a SPARQL query');
      });
    });

    describe('the WikiProject source', () => {
      beforeEach(() => {
        cy.get('#source-wikiproject').click();
      });

      it('restricts the project to en.wikipedia.org', () => {
        cy.get('#project-select option').should('have.length', 1);
        cy.get('#project-select').should('have.value', 'en.wikipedia.org');
      });

      it('adds and removes projects with the autocomplete', () => {
        cy.get('#include-items input[type=text]').type('Water');
        cy.get('#include-items li').first().click();
        cy.get('#include-projects').contains('Water');
        cy.get('#include-projects button').first().click();
        cy.get('#include-projects').should('not.exist');
      });

      it('requires at least one included project', () => {
        cy.get('#name-input').type('WikiProject List');
        cy.get('#saveListButton').click();
        cy.contains('Please provide at least one WikiProject to include.');
      });

      it('saves include and exclude lists', () => {
        cy.intercept('POST', 'v1/builders/', (req) => {
          expect(req.body.model).to.equal('wp1.selection.models.wikiproject');
          expect(req.body.params.include).to.have.length(1);
          expect(req.body.params.exclude).to.have.length(1);
          req.reply({
            statusCode: 200,
            body: { success: true, id: 'new-id-3', items: {} },
          });
        }).as('save');
        cy.get('#name-input').type('WikiProject List');
        cy.get('#include-items input[type=text]').type('Water');
        cy.get('#include-items li').first().click();
        cy.get('#exclude-items input[type=text]').type('Alien');
        cy.get('#exclude-items li').first().click();
        cy.get('#saveListButton').click();
        cy.wait('@save');
        cy.url().should('include', '/selections/user/new-id-3');
      });
    });

    describe('the Petscan and Book sources', () => {
      it('saves a petscan URL', () => {
        cy.get('#source-petscan').click();
        cy.intercept('POST', 'v1/builders/', (req) => {
          expect(req.body.model).to.equal('wp1.selection.models.petscan');
          expect(req.body.params.url).to.contain('psid');
          req.reply({
            statusCode: 200,
            body: { success: true, id: 'new-id-4', items: {} },
          });
        }).as('save');
        cy.get('#name-input').type('Petscan List');
        cy.get('#petscan-url').type('https://petscan.wmcloud.org/?psid=123');
        cy.get('#saveListButton').click();
        cy.wait('@save');
        cy.url().should('include', '/selections/user/new-id-4');
      });

      it('saves a book URL', () => {
        cy.get('#source-book').click();
        cy.intercept('POST', 'v1/builders/', (req) => {
          expect(req.body.model).to.equal('wp1.selection.models.book');
          req.reply({
            statusCode: 200,
            body: { success: true, id: 'new-id-5', items: {} },
          });
        }).as('save');
        cy.get('#name-input').type('Book List');
        cy.get('#book-url').type(
          'https://en.wikipedia.org/wiki/Book:Trees_of_the_World'
        );
        cy.get('#saveListButton').click();
        cy.wait('@save');
        cy.url().should('include', '/selections/user/new-id-5');
      });
    });
  });

  describe('old create URLs', () => {
    beforeEach(() => {
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
    });

    it('redirects /selections/simple to the unified flow', () => {
      cy.visit('/#/selections/simple');
      cy.url().should('include', '/selections/new');
      cy.url().should('include', 'source=simple');
      cy.contains('h1', 'New simple selection');
    });

    it('redirects /selections/sparql with the source preselected', () => {
      cy.visit('/#/selections/sparql');
      cy.contains('h1', 'New SPARQL selection');
    });

    it('redirects /selections/wikiproject with the source preselected', () => {
      cy.visit('/#/selections/wikiproject');
      cy.contains('h1', 'New WikiProject selection');
    });
  });

  describe('when the user is not logged in', () => {
    it('shows the signed-out explanation', () => {
      cy.visit('/#/selections/new');
      cy.contains('a', 'Sign in with Wikipedia');
    });
  });
});
