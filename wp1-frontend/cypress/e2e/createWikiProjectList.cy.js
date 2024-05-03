/// <reference types="Cypress" />

describe('the create WikiProject builder page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
      cy.visit('/#/selections/wikiproject');
    });

    it('successfully loads', () => {});

    it('displays only en.wikipedia.org', () => {
      cy.get('select').contains('en.wikipedia.org');
      cy.get('select').find('option').should('have.length', 1);
    });

    it('validates list name on clicking save', () => {
      cy.get('#saveListButton').click();
      cy.get('#listName').contains('Please provide a valid list name');
    });

    it('validates textbox on clicking save', () => {
      cy.get('#saveListButton').click();
      cy.get('#listName > .invalid-feedback').should('be.visible');
      cy.get('#include-items ~ .invalid-feedback').should('be.visible');
    });

    it('validates list name on losing focus', () => {
      cy.get('#listName > .form-control').click();
      cy.get('#include-items').click();
      cy.get('#listName > .invalid-feedback').should('be.visible');
    });

    it('displays a textbox with invalid wikiProjects', () => {
      cy.get('#listName > .form-control').click().type('List name');
      cy.get('#include-items').click().type('Fake Project 1\nAnother Fake');
      cy.intercept('v1/builders/', {
        fixture: 'save_wikiproject_failure.json',
      });
      cy.get('#saveListButton').click();

      cy.get('#include-items').should(
        'have.value',
        'Fake Project 1\nAnother Fake',
      );
      cy.get('#invalid_articles > .form-control').should(
        'have.value',
        'Fake Project 1\nAnother Fake',
      );
    });

    it('saves successfully after fixing invalid names', () => {
      let count = 0;
      cy.intercept('v1/builders/', (req) => {
        if (count === 0) {
          // First request fails.
          count++;
          req.reply({
            statusCode: 200,
            fixture: 'save_wikiproject_failure.json',
          });
        } else {
          req.reply({
            statusCode: 200,
            fixture: 'save_list_success.json',
          });
        }
      });

      cy.get('#listName > .form-control').click().type('List Name');
      cy.get('#include-items').click().type('Fake Project 1\nAnother Fake');
      cy.get('#saveListButton').click();
      cy.get('#saveListButton').click();
      cy.url().should('eq', 'http://localhost:5173/#/selections/user');
    });

    describe('when save button clicked', () => {
      beforeEach(() => {
        cy.intercept('v1/builders/', (req) => {
          req.continue(() => {
            return new Promise((resolve) => {
              setTimeout(resolve, 4000);
            });
          });
        });
      });

      it('shows spinner', () => {
        cy.get('#listName > .form-control').click().type('List Name');
        cy.get('#include-items').click().type('Fake Project');
        cy.get('#saveListButton').click();
        cy.get('#saveLoader').should('be.visible');
      });

      it('disables save button', () => {
        cy.get('#listName > .form-control').click().type('List Name');
        cy.get('#include-items').click().type('Fake Project');
        cy.get('#saveListButton').click();
        cy.get('#saveListButton').should('have.attr', 'disabled');
      });
    });

    it('redirects on saving valid project names', () => {
      cy.get('#listName > .form-control').click().type('List Name');
      cy.get('#include-items').click().type('Fake Project\nAnother Fake');
      cy.intercept('v1/builders/', { fixture: 'save_list_success.json' });
      cy.get('#saveListButton').click();
      cy.url().should('eq', 'http://localhost:5173/#/selections/user');
    });
  });

  describe('when the user is not logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/sites/', { fixture: 'sites.json' });
    });

    it('opens login page', () => {
      cy.visit('/#/selections/simple');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
