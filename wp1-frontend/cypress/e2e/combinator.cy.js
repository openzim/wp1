/// <reference types="Cypress" />

describe('the combinator builder page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'login'
      );
      cy.intercept('v1/selection/lists', {
        fixture: 'combinator_lists.json',
      }).as('list');
    });

    describe('creating a new combinator', () => {
      beforeEach(() => {
        cy.visit('/#/selections/combinator');
        cy.wait('@login');
        cy.wait('@list');
      });

      it('successfully loads', () => {
        cy.contains('h1', 'New combinator selection');
      });

      it('shows eligible selections in the library', () => {
        cy.contains('Simple Ready');
        cy.contains('SPARQL Ready');
        // Combinators can't be nested.
        cy.contains('Existing Combinator').should('not.exist');
        // Other-project selections are excluded.
        cy.contains('German Simple').should('not.exist');
      });

      it('shows the library count', () => {
        cy.contains('2 total');
      });

      it('filters the library by search', () => {
        cy.get('input[aria-label="Filter your selections"]').type('sparql');
        cy.contains('SPARQL Ready');
        cy.contains('Simple Ready').should('not.exist');
      });

      it('filters the library by type pill', () => {
        cy.contains('button', 'Simple').click();
        cy.contains('Simple Ready');
        cy.contains('SPARQL Ready').should('not.exist');
        cy.contains('button', 'All types').click();
        cy.contains('SPARQL Ready');
      });

      it('shows German selections when the project changes', () => {
        cy.intercept('v1/sites/', {
          body: {
            sites: ['de.wikipedia.org', 'en.wikipedia.org'],
          },
        });
        // Reload so the new sites list is fetched.
        cy.reload();
        cy.get('#combinator-project').select('de.wikipedia.org');
        cy.contains('German Simple');
        cy.contains('Simple Ready').should('not.exist');
      });

      it('adds selections to include and exclude groups', () => {
        cy.contains('Simple Ready')
          .parent()
          .within(() => cy.contains('button', 'include').click());
        cy.get('#include-items').contains('Simple Ready');

        cy.contains('SPARQL Ready')
          .parent()
          .within(() => cy.contains('button', 'exclude').click());
        cy.get('#exclude-items').contains('SPARQL Ready');
      });

      it('moves a selection between groups', () => {
        cy.contains('Simple Ready')
          .parent()
          .within(() => cy.contains('button', 'include').click());
        cy.get('#include-items').contains('button', '→ exclude').click();
        cy.get('#exclude-items').contains('Simple Ready');
      });

      it('removes a selection and returns it to the library', () => {
        cy.contains('Simple Ready')
          .parent()
          .within(() => cy.contains('button', 'include').click());
        cy.get('#include-items')
          .get('button[aria-label="Remove Simple Ready"]')
          .click();
        cy.get('#include-items').contains('Add selections from the left');
        cy.contains('Simple Ready');
      });

      it('builds the expression and sentence', () => {
        cy.contains('Add at least one selection to include.');
        cy.contains('Simple Ready')
          .parent()
          .within(() => cy.contains('button', 'include').click());
        cy.contains('Take every article from 1 included selection.');
        cy.get('#expression-preview').contains('Simple Ready');

        cy.contains('SPARQL Ready')
          .parent()
          .within(() => cy.contains('button', 'exclude').click());
        cy.get('#expression-preview').contains('Simple Ready NOT SPARQL Ready');
      });

      it('toggles OR/AND logic per group', () => {
        cy.contains('Simple Ready')
          .parent()
          .within(() => cy.contains('button', 'include').click());
        cy.get('#include-operation').contains('OR · any article');
        cy.contains('Take every article from 1 included selection.');
        cy.get('#include-operation').click();
        cy.get('#include-operation').contains('AND · only shared');
        cy.contains(
          'Take the articles that appear in every one of 1 included selection.'
        );
      });

      it('disables save until a name and an included selection exist', () => {
        cy.get('#saveListButton').should('have.attr', 'disabled');
        cy.contains(
          'Name the selection and add at least one selection to include'
        );
        cy.get('#combinator-name').type('My Combinator');
        cy.contains('Add at least one selection to include before saving.');
        cy.contains('Simple Ready')
          .parent()
          .within(() => cy.contains('button', 'include').click());
        cy.get('#saveListButton').should('not.have.attr', 'disabled');
      });

      it('saves the combinator and redirects to its detail pane', () => {
        cy.intercept('POST', 'v1/builders/', (req) => {
          expect(req.body.model).to.equal('wp1.selection.models.combinator');
          expect(req.body.params.include.builders).to.deep.equal([
            'simple-ready',
          ]);
          expect(req.body.params.include.operation).to.equal('union');
          expect(req.body.params.exclude.builders).to.deep.equal([
            'sparql-ready',
          ]);
          req.reply({
            statusCode: 200,
            body: { success: true, id: 'combo-new', items: {} },
          });
        }).as('save');

        cy.get('#combinator-name').type('My Combinator');
        cy.contains('Simple Ready')
          .parent()
          .within(() => cy.contains('button', 'include').click());
        cy.contains('SPARQL Ready')
          .parent()
          .within(() => cy.contains('button', 'exclude').click());
        cy.get('#saveListButton').click();
        cy.wait('@save');
        cy.url().should('include', '/selections/user/combo-new');
      });

      it('shows API errors on save failure', () => {
        cy.intercept('POST', 'v1/builders/', {
          fixture: 'save_combinator_failure.json',
        }).as('save');
        cy.get('#combinator-name').type('My Combinator');
        cy.contains('Simple Ready')
          .parent()
          .within(() => cy.contains('button', 'include').click());
        cy.get('#saveListButton').click();
        cy.wait('@save');
        cy.get('#saveListButton').should('not.have.attr', 'disabled');
      });
    });

    describe('editing an existing combinator', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/combo-1', {
          fixture: 'combinator_builder.json',
        }).as('builder');
        cy.visit('/#/selections/combinator/combo-1');
        cy.wait('@login');
        cy.wait('@list');
        cy.wait('@builder');
      });

      it('loads the recipe from the builder params', () => {
        cy.contains('h1', 'Edit combinator selection');
        cy.get('#combinator-name').should('have.value', 'Combinator Builder');
        cy.get('#include-items').contains('Simple Ready');
        cy.get('#exclude-items').contains('SPARQL Ready');
        cy.get('#include-operation').contains('AND · only shared');
        cy.get('#exclude-operation').contains('OR · any article');
      });

      it('saves updates to the same builder', () => {
        cy.intercept('POST', 'v1/builders/combo-1', (req) => {
          expect(req.body.params.include.operation).to.equal('union');
          req.reply({
            statusCode: 200,
            body: { success: true, id: 'combo-1', items: {} },
          });
        }).as('save');
        cy.get('#include-operation').click();
        cy.get('#saveListButton').click();
        cy.wait('@save');
        cy.url().should('include', '/selections/user/combo-1');
      });
    });

    describe('when the builder is not found', () => {
      it('shows the 404 message', () => {
        cy.intercept('GET', 'v1/builders/missing', {
          statusCode: 404,
          body: '404 NOT FOUND',
        });
        cy.visit('/#/selections/combinator/missing');
        cy.contains('404 Not Found');
      });
    });
  });

  describe('when the user is not logged in', () => {
    it('shows the signed-out explanation', () => {
      cy.visit('/#/selections/combinator');
      cy.contains('a', 'Sign in with Wikipedia');
    });
  });
});
