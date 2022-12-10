/// <reference types="Cypress" />

describe('the update SPARQL list page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' }).as('sites');
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'identity'
      );
    });

    describe('and the builder is found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/2', {
          fixture: 'sparql_builder.json',
        }).as('builder');
        cy.visit('/#/selections/sparql/2');
        cy.wait('@sites');
        cy.wait('@identity');
        cy.wait('@builder');
      });

      it('successfully loads', () => {});

      it('displays wiki projects', () => {
        cy.get('select').contains('aa.wikipedia.org');
        cy.get('select').contains('en.wiktionary.org');
        cy.get('select').contains('en.wikipedia.org');
      });

      it('displays builder information', () => {
        cy.get('#listName > .form-control').should('have.value', 'Builder 2');
        cy.get('#items > .form-control').should(
          'have.value',
          'SELECT ?foo WHERE {}'
        );
        cy.get('#project > select').should('have.value', 'en.wiktionary.org');
      });

      it('displays server validation errors', () => {
        cy.get('#listName > .form-control').click().type('List Name');
        cy.get('#items > .form-control').click().clear().type('SELECT ?foo');

        cy.intercept('v1/builders/2', { fixture: 'save_sparql_failure.json' });
        cy.get('#updateListButton').click();

        cy.get('#items > .form-control').should('have.value', 'SELECT ?foo');
        cy.get('.errors').contains('The query was not valid');
      });

      it('saves successfully after fixing invalid query', () => {
        cy.intercept('v1/builders/2', (req) => {
          if (req.body.params.query.indexOf('WHERE') === -1) {
            // First request is missing a WHERE clause.
            req.reply({
              statusCode: 200,
              fixture: 'save_sparql_failure.json',
            });
          } else {
            // Second request has WHERE and is valid.
            req.reply({
              statusCode: 200,
              fixture: 'save_sparql_success.json',
            });
          }
        });

        cy.get('#listName > .form-control').click().type('List Name');
        cy.get('#items > .form-control').click().clear().type('SELECT ?foo');
        cy.get('#updateListButton').click();

        cy.get('#items > .form-control')
          .click()
          .clear()
          .type('SELECT ?foo WHERE {}', { parseSpecialCharSequences: false });

        cy.get('#updateListButton').click();
        cy.url().should('eq', 'http://localhost:5173/#/selections/user');
      });

      describe('on update success', () => {
        beforeEach(() => {
          cy.intercept('POST', 'v1/builders/2', {
            fixture: 'save_list_success.json',
          });
        });

        it('redirects on saving valid article names', () => {
          cy.intercept('v1/builders/2', { fixture: 'save_list_success.json' });
          cy.get('#updateListButton').click();
          cy.url().should('eq', 'http://localhost:5173/#/selections/user');
        });
      });

      describe('when update button clicked', () => {
        beforeEach(() => {
          cy.intercept('POST', 'v1/builders/2', (req) => {
            req.continue(() => {
              return new Promise((resolve) => {
                setTimeout(resolve, 4000);
              });
            });
          });
        });

        it('shows spinner', () => {
          cy.get('#updateListButton').click();
          cy.get('#updateLoader').should('be.visible');
        });

        it('disables update button', () => {
          cy.get('#updateListButton').click();
          cy.get('#updateListButton').should('have.attr', 'disabled');
        });
      });
    });

    describe('and the builder has fatal errors', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          fixture: 'sparql_builder_fatal_error.json',
        });
        cy.visit('/#/selections/simple/1');
      });

      it('displays the error div', () => {
        cy.get('.materialize-error').should('be.visible');
      });

      it('disables the retry button', () => {
        cy.get('.materialize-error .btn').should('have.attr', 'disabled');
      });
    });

    describe('and the builder has retryable errors', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          fixture: 'sparql_builder_retryable_error.json',
        });
        cy.visit('/#/selections/simple/1');
      });

      it('displays the error div', () => {
        cy.get('.materialize-error').should('be.visible');
      });

      it('enables the retry button', () => {
        cy.get('.materialize-error .btn').should('not.have.attr', 'disabled');
      });
    });

    describe('and the builder is not found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/2', {
          statusCode: 404,
          body: '404 NOT FOUND',
        });
        cy.visit('/#/selections/sparql/2');
      });

      it('displays the 404 text', () => {
        cy.get('#404').should('be.visible');
      });
    });
  });

  describe('when the user is not logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
    });

    it('opens login page', () => {
      cy.visit('/#/selections/sparql/2');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
