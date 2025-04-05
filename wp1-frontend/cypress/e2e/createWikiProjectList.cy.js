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

    it('validates input on clicking save', () => {
      cy.get('#saveListButton').click();
      cy.get('#listName > .invalid-feedback').should('be.visible');
      cy.get('#lists .invalid-feedback').should('be.visible')
      cy.get('#include-items').find('.invalid-feedback').should('be.visible');
    });

    it('validates list name on losing focus', () => {
      cy.get('#listName > .form-control').click();
      cy.get('#include-items').click();
      cy.get('#listName > .invalid-feedback').should('be.visible');
    });

    it('displays a textbox with invalid wikiProjects', () => {
      cy.get('#listName > .form-control').click();
      cy.get('#listName > .form-control').type('List name');
      cy.get('#include-items').click();
      cy.intercept('v1/builders/', (req) => {
        req.reply({
          statusCode: 200,
          fixture: 'save_wikiproject_failure.json',
        });
    });
      cy.get('#include-items').type('Fake Project\n');
      cy.get('#include-projects').children().eq(0).should('contain.text', 'Fake Project');
      cy.get('#invalid_articles > .form-control').should(
        'have.value',
        'Fake Project',
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

      cy.get('#listName > .form-control').click();
      cy.get('#listName > .form-control').type('List Name');
      cy.get('#include-items').click();
      cy.get('#include-items').type('Water\n');
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
        cy.get('#listName > .form-control').click();
        cy.get('#listName > .form-control').type('List Name');
        
        cy.get('#include-items').find('.search').type('Alien');
        cy.get('#include-items').find('.results').should('be.visible');
        cy.get('#include-items').find('.results').children('li').eq(0).should('contain.text', 'Alien');
        cy.get('#include-items').find('.results').children('li').eq(0).click();
        
        cy.get('#saveListButton').click();
        cy.get('#saveLoader').should('be.visible');
      });

      it('disables save button', () => {
        cy.get('#listName > .form-control').click();
        cy.get('#listName > .form-control').type('List Name');
        
        cy.get('#include-items').find('.search').type('Alien');
        cy.get('#include-items').find('.results').should('be.visible');
        cy.get('#include-items').find('.results').children('li').eq(0).should('contain.text', 'Alien');
        cy.get('#include-items').find('.results').children('li').eq(0).click();
        
        cy.get('#saveListButton').click();
        cy.get('#saveListButton').should('have.attr', 'disabled');
      });
    });

    it('redirects on saving valid project names', () => {
      cy.get('#listName > .form-control').click();
      cy.get('#listName > .form-control').type('List Name');
      
      cy.get('#include-items').find('.search').type('Alien');
      cy.get('#include-items').find('.results').should('be.visible');
      cy.get('#include-items').find('.results').children('li').eq(0).should('contain.text', 'Alien');
      cy.get('#include-items').find('.results').children('li').eq(0).click();

      cy.intercept('v1/builders/', { fixture: 'save_list_success.json' }).as(
        'createBuilderSuccess',
      );
      cy.get('#saveListButton').click();
      cy.wait('@createBuilderSuccess');
      cy.url().should('eq', 'http://localhost:5173/#/selections/user');
    });

    it('sends correct data to API', () => {
      cy.get('#listName > .form-control').click();
      cy.get('#listName > .form-control').type('List Name');
      
      cy.get('#include-items').find('.search').type('Alien');
      cy.get('#include-items').find('.results').should('be.visible');
      cy.get('#include-items').find('.results').children('li').eq(0).should('contain.text', 'Alien');
      cy.get('#include-items').find('.results').children('li').eq(0).click();

      cy.get('#exclude-items').find('.search').type('Barbados');
      cy.get('#exclude-items').find('.results').should('be.visible');
      cy.get('#exclude-items').find('.results').children('li').eq(0).should('contain.text', 'Barbados');
      cy.get('#exclude-items').find('.results').children('li').eq(0).click();

      cy.intercept('v1/builders/', { fixture: 'save_list_success.json' }).as(
        'createBuilderSuccess',
      );
      cy.get('#saveListButton').click();
      cy.wait('@createBuilderSuccess').then((interception) => {
        expect(interception.request.body.params.include).to.deep.equal([
          'Alien',
        ]);
        expect(interception.request.body.params.exclude).to.deep.equal([
          'Barbados',
        ]);
      });
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
