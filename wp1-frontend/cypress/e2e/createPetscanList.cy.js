/// <reference types="Cypress" />

describe('the petscan builder page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
    });

    describe('creating a new selection', () => {
      beforeEach(() => {
        cy.visit('/#/selections/petscan');
      });

      it('successfully loads', () => {});

      it('displays wiki projects', () => {
        cy.get('select').contains('aa.wikipedia.org');
        cy.get('select').contains('en.wiktionary.org');
        cy.get('select').contains('en.wikipedia.org');
      });

      it('validates list name on clicking save', () => {
        cy.get('#saveListButton').click();
        cy.get('#listName').contains('Please provide a valid list name');
        cy.get('#listName > .invalid-feedback').should('be.visible');
      });

      it('shows URL validation error from the server', () => {
        cy.get('#listName > .form-control').click().type('My List');
        cy.get('#petscanUrl').click().type('not-a-petscan-url');
        cy.intercept('v1/builders/', { fixture: 'save_petscan_failure.json' });
        cy.get('#saveListButton').click();
        cy.get('#items > .invalid-feedback').should('be.visible');
        cy.get('#invalid_articles').contains('Invalid PetScan URL');
      });

      it('redirects on successful save', () => {
        cy.get('#listName > .form-control').click().type('My List');
        cy.get('#petscanUrl')
          .click()
          .type('https://petscan.wmflabs.org/?psid=123456');
        cy.intercept('v1/builders/', { fixture: 'save_list_success.json' });
        cy.get('#saveListButton').click();
        cy.url().should('eq', 'http://localhost:5173/#/selections/user');
      });

      it('sends correct data to the API', () => {
        cy.get('#listName > .form-control').click().type('My List');
        cy.get('#petscanUrl')
          .click()
          .type('https://petscan.wmflabs.org/?psid=123456');
        cy.intercept('v1/builders/', { fixture: 'save_list_success.json' }).as(
          'saveBuilder'
        );
        cy.get('#saveListButton').click();
        cy.wait('@saveBuilder').then((interception) => {
          expect(interception.request.body.model).to.equal(
            'wp1.selection.models.petscan'
          );
          expect(interception.request.body.params.url).to.equal(
            'https://petscan.wmflabs.org/?psid=123456'
          );
        });
      });

      describe('when save button clicked', () => {
        beforeEach(() => {
          // Delayed reply keeps the spinner visible to assert on.
          cy.intercept('v1/builders/', {
            delay: 4000,
            statusCode: 200,
            fixture: 'save_list_success.json',
          });
          cy.get('#listName > .form-control').click().type('My List');
          cy.get('#petscanUrl')
            .click()
            .type('https://petscan.wmflabs.org/?psid=123456');
          cy.get('#saveListButton').click();
        });

        it('shows spinner', () => {
          cy.get('#saveLoader').should('be.visible');
        });

        it('disables save button', () => {
          cy.get('#saveListButton').should('have.attr', 'disabled');
        });
      });
    });

    describe('editing an existing selection', () => {
      describe('and the builder is found', () => {
        beforeEach(() => {
          cy.intercept('GET', 'v1/builders/3', {
            fixture: 'petscan_builder.json',
          }).as('builder');
          cy.visit('/#/selections/petscan/3');
          cy.wait('@builder');
        });

        it('displays builder information', () => {
          cy.get('#listName > .form-control').should(
            'have.value',
            'Petscan Builder'
          );
          cy.get('#petscanUrl').should(
            'have.value',
            'https://petscan.wmflabs.org/?psid=123456'
          );
        });

        it('sends correct data to the API on update', () => {
          cy.intercept('POST', 'v1/builders/3', {
            fixture: 'save_list_success.json',
          }).as('updateBuilder');
          cy.get('#updateListButton').click();
          cy.wait('@updateBuilder').then((interception) => {
            expect(interception.request.body.params.url).to.equal(
              'https://petscan.wmflabs.org/?psid=123456'
            );
          });
        });

        it('redirects on successful update', () => {
          cy.intercept('POST', 'v1/builders/3', {
            fixture: 'save_list_success.json',
          });
          cy.get('#updateListButton').click();
          cy.url().should('eq', 'http://localhost:5173/#/selections/user');
        });
      });

      describe('and the builder has fatal errors', () => {
        beforeEach(() => {
          cy.intercept('GET', 'v1/builders/3', {
            fixture: 'petscan_builder_fatal_error.json',
          });
          cy.visit('/#/selections/petscan/3');
        });

        it('displays the error div with a disabled retry button', () => {
          cy.get('.materialize-error').should('be.visible');
          cy.get('.materialize-error .btn').should('have.attr', 'disabled');
        });
      });

      describe('and the builder has retryable errors', () => {
        beforeEach(() => {
          cy.intercept('GET', 'v1/builders/3', {
            fixture: 'petscan_builder_retryable_error.json',
          });
          cy.visit('/#/selections/petscan/3');
        });

        it('displays the error div with an enabled retry button', () => {
          cy.get('.materialize-error').should('be.visible');
          cy.get('.materialize-error .btn').should('not.have.attr', 'disabled');
        });
      });

      describe('and the builder is not found', () => {
        beforeEach(() => {
          cy.intercept('GET', 'v1/builders/3', {
            statusCode: 404,
            body: '404 NOT FOUND',
          });
          cy.visit('/#/selections/petscan/3');
        });

        it('displays the 404 text', () => {
          cy.get('#404').should('be.visible');
        });
      });
    });
  });

  describe('when the user is not logged in', () => {
    it('opens login page', () => {
      cy.visit('/#/selections/petscan');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
