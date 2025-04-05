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
        cy.intercept('GET', 'v1/builders/3', {
          fixture: 'wikiproject_builder.json',
        }).as('builder');
        cy.visit('/#/selections/wikiproject/3');
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
        cy.get('#listName > .form-control').should('have.value', 'Builder 3');
        cy.get('#include-projects').children().should('have.length', 2);
        cy.get('#include-projects').children().eq(0).should('contain.text', 'British Columbia road transport');
        cy.get('#include-projects').children().eq(1).should('contain.text', 'New Brunswick road transport');
        cy.get('#exclude-projects').children().should('have.length', 1);
        cy.get('#exclude-projects').children().eq(0).should('contain.text', 'Countries');
        cy.get('#project > select').should('have.value', 'en.wikipedia.org');
      });

      it('does not show invalid list name', () => {
        cy.get('#listName > .invalid-feedback').should('not.be.visible');
      });

      it('displays a textbox with invalid project names', () => {
        cy.intercept('v1/builders/3', {
          fixture: 'save_wikiproject_failure.json',
        });
        cy.get('#updateListButton').click();

        cy.get('#invalid_articles > .form-control').should(
          'have.value',
          'Fake Project',
        );
      });

      it('sends correct data to API', () => {
        cy.intercept('v1/builders/3', { fixture: 'save_list_success.json' }).as(
          'updateBuilderSuccess',
        );
        cy.get('#updateListButton').click();
        cy.wait('@updateBuilderSuccess').then((interception) => {
          expect(interception.request.body.params.include).to.deep.equal([
            'British Columbia road transport',
            'New Brunswick road transport',
          ]);
          expect(interception.request.body.params.exclude).to.deep.equal([
            'Countries',
          ]);
        });
      });

      it('redirects on saving valid project names', () => {
        cy.intercept('POST', 'v1/builders/3', {
          fixture: 'save_list_success.json',
        });
        cy.get('#updateListButton').click();
        cy.url().should('eq', 'http://localhost:5173/#/selections/user');
      });

      describe('when update button clicked', () => {
        beforeEach(() => {
          cy.intercept('POST', 'v1/builders/3', (req) => {
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
        cy.intercept('GET', 'v1/builders/3', {
          fixture: 'wikiproject_builder_fatal_error.json',
        });
        cy.visit('/#/selections/wikiproject/3');
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
        cy.intercept('GET', 'v1/builders/3', {
          fixture: 'wikiproject_builder_retryable_error.json',
        });
        cy.visit('/#/selections/wikiproject/3');
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
        cy.intercept('GET', 'v1/builders/3', {
          statusCode: 404,
          body: '404 NOT FOUND',
        });
        cy.visit('/#/selections/wikiproject/3');
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
      cy.visit('/#/selections/wikiproject/3');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
