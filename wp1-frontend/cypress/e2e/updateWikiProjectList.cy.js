/// <reference types="Cypress" />

describe('the update wikiproject list page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' }).as('sites');
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'identity',
      );
    });

    describe('and the builder is found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          fixture: 'wikiproject_builder.json',
        }).as('builder');
        cy.visit('/#/selections/wikiproject/1');
        cy.wait('@sites');
        cy.wait('@identity');
        cy.wait('@builder');
      });

      it('successfully loads', () => {});

      it('displays only en.wikipedia.org', () => {
        cy.get('select').contains('en.wikipedia.org');
        cy.get('select').find('option').should('have.length', 1);
      });

      it('displays builder information', () => {
        cy.get('#listName > .form-control').should('have.value', 'Builder 1');
        cy.get('#add-items').should(
          'have.value',
          'British Columbia road transport\nNew Brunswick road transport',
        );
        cy.get('#project > select').should('have.value', 'en.wikipedia.org');
      });

      it('does not show invalid list items', () => {
        cy.get('#add-items ~ .invalid-feedback').should('not.be.visible');
      });

      it('does not show invalid list name', () => {
        cy.get('#listName > .invalid-feedback').should('not.be.visible');
      });

      it('displays a textbox with invalid project names', () => {
        cy.intercept('v1/builders/1', {
          fixture: 'save_wikiproject_failure.json',
        });
        cy.get('#updateListButton').click();

        cy.get('#invalid_articles > .form-control').should(
          'have.value',
          'Fake Project 1\nAnother Fake',
        );
      });

      it('redirects on saving valid project names', () => {
        cy.intercept('POST', 'v1/builders/1', {
          fixture: 'save_list_success.json',
        });
        cy.get('#updateListButton').click();
        cy.url().should('eq', 'http://localhost:5173/#/selections/user');
      });

      describe('when update button clicked', () => {
        beforeEach(() => {
          cy.intercept('POST', 'v1/builders/1', (req) => {
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
          fixture: 'wikiproject_builder_fatal_error.json',
        });
        cy.visit('/#/selections/wikiproject/1');
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
          fixture: 'wikiproject_builder_retryable_error.json',
        });
        cy.visit('/#/selections/wikiproject/1');
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
        cy.intercept('GET', 'v1/builders/1', {
          statusCode: 404,
          body: '404 NOT FOUND',
        });
        cy.visit('/#/selections/wikiproject/1');
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
      cy.visit('/#/selections/wikiproject/1');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
