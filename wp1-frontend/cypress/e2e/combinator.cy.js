/// <reference types="Cypress" />

describe('the combinator builder page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' }).as('sites');
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'identity'
      );
      cy.intercept('v1/selection/simple/lists', {
        fixture: 'combinator_lists.json',
      }).as('lists');
    });

    it('loads create form with eligible builders only', () => {
      cy.visit('/#/selections/combinator');
      cy.wait('@lists');

      cy.get('#include-builder-select').should('contain', 'Simple Ready');
      cy.get('#include-builder-select').should('contain', 'SPARQL Ready');
      cy.get('#include-builder-select').should('not.contain', 'German Simple');
      cy.get('#include-builder-select').should(
        'not.contain',
        'Existing Combinator'
      );
      cy.get('#exclude-builder-select').should('contain', 'Simple Ready');
      cy.get('#exclude-builder-select').should('contain', 'SPARQL Ready');
      cy.get('#exclude-builder-select').should('not.contain', 'German Simple');
      cy.get('#exclude-builder-select').should(
        'not.contain',
        'Existing Combinator'
      );
    });

    it('displays builder loading errors', () => {
      cy.intercept('v1/selection/simple/lists', {
        statusCode: 500,
        body: {},
      }).as('listsFailure');

      cy.visit('/#/selections/combinator');
      cy.wait('@listsFailure');

      cy.get('.alert-danger')
        .should('be.visible')
        .and('contain', 'Unable to load builders. Please try again later.');
      cy.contains('No builders are available').should('not.exist');
    });

    it('validates that at least one include builder is selected', () => {
      cy.visit('/#/selections/combinator');
      cy.wait('@lists');

      cy.get('#listName > .form-control').click().type('Combined List');
      cy.get('#saveListButton').click();

      cy.get('#include-items .invalid-feedback').should('be.visible');
    });

    it('validates selected builders belong to the selected project', () => {
      cy.visit('/#/selections/combinator');
      cy.wait('@lists');

      cy.get('#listName > .form-control').click().type('Combined List');
      cy.get('#include-builder-select').select('simple-ready');
      cy.get('#add-include-builder').click();
      cy.get('#project > select').select('en.wiktionary.org');
      cy.get('#saveListButton').click();

      cy.get('#include-items .invalid-feedback')
        .should('be.visible')
        .and('contain', 'Simple Ready (en.wikipedia.org)');
    });

    it('displays backend validation errors', () => {
      cy.visit('/#/selections/combinator');
      cy.wait('@lists');

      cy.get('#listName > .form-control').click().type('Combined List');
      cy.get('#include-builder-select').select('simple-ready');
      cy.get('#add-include-builder').click();
      cy.intercept('POST', 'v1/builders/', {
        fixture: 'save_combinator_failure.json',
      }).as('createBuilderFailure');
      cy.get('#saveListButton').click();

      cy.wait('@createBuilderFailure');
      cy.get('.errors').contains(
        "Builder 'missing-builder' no longer exists. Please remove it from this combinator."
      );
    });

    it('sends correct create payload to the API', () => {
      cy.visit('/#/selections/combinator');
      cy.wait('@lists');

      cy.get('#listName > .form-control').click().type('Combined List');
      cy.get('#include-operation').select('intersection');
      cy.get('#include-builder-select').select('simple-ready');
      cy.get('#add-include-builder').click();
      cy.get('#exclude-operation').select('union');
      cy.get('#exclude-builder-select').select('sparql-ready');
      cy.get('#add-exclude-builder').click();

      cy.intercept('POST', 'v1/builders/', {
        fixture: 'save_list_success.json',
      }).as('createBuilderSuccess');
      cy.get('#saveListButton').click();

      cy.wait('@createBuilderSuccess').then((interception) => {
        expect(interception.request.body.model).to.equal(
          'wp1.selection.models.combinator'
        );
        expect(interception.request.body.params.include).to.deep.equal({
          builders: ['simple-ready'],
          operation: 'intersection',
        });
        expect(interception.request.body.params.exclude).to.deep.equal({
          builders: ['sparql-ready'],
          operation: 'union',
        });
      });
    });

    it('loads and updates an existing combinator', () => {
      cy.intercept('GET', 'v1/builders/combo-1', {
        fixture: 'combinator_builder.json',
      }).as('builder');
      cy.visit('/#/selections/combinator/combo-1');
      cy.wait('@builder');
      cy.wait('@lists');

      cy.get('#listName > .form-control').should(
        'have.value',
        'Combinator Builder'
      );
      cy.get('#include-builders').should('contain', 'Simple Ready');
      cy.get('#exclude-builders').should('contain', 'SPARQL Ready');
      cy.get('#include-operation').should('have.value', 'intersection');
      cy.get('#exclude-operation').should('have.value', 'union');
      cy.get('#include-builder-select').should(
        'not.contain',
        'Existing Combinator'
      );

      cy.intercept('POST', 'v1/builders/combo-1', {
        fixture: 'save_list_success.json',
      }).as('updateBuilderSuccess');
      cy.get('#updateListButton').click();

      cy.wait('@updateBuilderSuccess').then((interception) => {
        expect(interception.request.body.params.include).to.deep.equal({
          builders: ['simple-ready'],
          operation: 'intersection',
        });
        expect(interception.request.body.params.exclude).to.deep.equal({
          builders: ['sparql-ready'],
          operation: 'union',
        });
      });
    });

    describe('when save button clicked', () => {
      beforeEach(() => {
        cy.visit('/#/selections/combinator');
        cy.wait('@lists');
        cy.get('#listName > .form-control').click().type('Combined List');
        cy.get('#include-builder-select').select('simple-ready');
        cy.get('#add-include-builder').click();
        cy.intercept('POST', 'v1/builders/', {
          delay: 4000,
          fixture: 'save_list_success.json',
        }).as('createBuilderSuccess');
      });

      it('shows spinner', () => {
        cy.get('#saveListButton').click();
        cy.get('#saveLoader').should('be.visible');
      });

      it('disables save button', () => {
        cy.get('#saveListButton').click();
        cy.get('#saveListButton').should('have.attr', 'disabled');
      });
    });

    describe('when the builder has fatal errors', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/combo-1', {
          fixture: 'combinator_builder_fatal_error.json',
        }).as('builder');
        cy.visit('/#/selections/combinator/combo-1');
        cy.wait('@builder');
      });

      it('displays the error div', () => {
        cy.get('.materialize-error').should('be.visible');
      });

      it('disables the retry button', () => {
        cy.get('.materialize-error .btn').should('have.attr', 'disabled');
      });
    });

    describe('when the builder has retryable errors', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/combo-1', {
          fixture: 'combinator_builder_retryable_error.json',
        }).as('builder');
        cy.visit('/#/selections/combinator/combo-1');
        cy.wait('@builder');
      });

      it('displays the error div', () => {
        cy.get('.materialize-error').should('be.visible');
      });

      it('enables the retry button', () => {
        cy.get('.materialize-error .btn').should('not.have.attr', 'disabled');
      });
    });

    describe('when the builder is not found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/missing-combo', {
          statusCode: 404,
          body: '404 NOT FOUND',
        }).as('builder');
        cy.visit('/#/selections/combinator/missing-combo');
        cy.wait('@builder');
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

    it('opens login page for create', () => {
      cy.visit('/#/selections/combinator');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });

    it('opens login page for edit', () => {
      cy.visit('/#/selections/combinator/combo-1');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
