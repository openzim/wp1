/// <reference types="Cypress" />

describe('the zim file creation page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'identity'
      );
    });

    describe('and the builder is found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          fixture: 'simple_builder.json',
        }).as('builder');
      });

      describe('when the zim file has not been requested yet', () => {
        beforeEach(() => {
          cy.intercept('v1/builders/1/zim/status', {
            fixture: 'zim_status_not_requested.json',
          }).as('status');
          cy.visit('/#/selections/1/zim');
          cy.wait('@identity');
          cy.wait('@builder');
          cy.wait('@status');
        });

        it('displays the form for entering descriptions', () => {
          cy.get('#desc').should('be.visible');
          cy.get('#longdesc').should('be.visible');
        });

        it('validates the description input on losing focus', () => {
          cy.get('#desc').click();
          cy.get('#longdesc').click();
          cy.get('#desc-group > .invalid-feedback').should('be.visible');
        });

        it('displays the Request ZIM file button', () => {
          cy.get('#request').should('be.visible');
          cy.get('#request').should('not.have.attr', 'disabled');
        });

        describe('when the description is missing and the submit button is clicked', () => {
          beforeEach(() => {
            cy.intercept('POST', 'v1/builders/1/zim', () => {
              throw new Error(
                'POST to create ZIM should not have been requested'
              );
            }).as('request');
          });

          it('does not submit the form', () => {
            cy.get('#request').click();
          });

          it('shows the error message', () => {
            cy.get('#request').click();
            cy.get('#desc-group > .invalid-feedback').should('be.visible');
          });
        });

        describe('when the Request ZIM file button is clicked', () => {
          beforeEach(() => {
            cy.intercept('POST', 'v1/builders/1/zim', {
              statusCode: 204,
            }).as('request');

            cy.get('#desc').click();
            cy.get('#desc').type('Description from user');
            cy.get('#request').click();
          });

          it('makes the ZIM file request', () => {
            cy.wait('@request');
          });
        });
      });

      describe('when the zim file has been requested but is not ready', () => {
        beforeEach(() => {
          cy.intercept('v1/builders/1/zim/status', {
            fixture: 'zim_status_not_ready.json',
          }).as('status');
          cy.visit('/#/selections/1/zim');
          cy.wait('@identity');
          cy.wait('@builder');
          cy.wait('@status');
        });

        it('does not display the form for descriptions', () => {
          cy.get('#desc').should('not.exist');
          cy.get('#longdesc').should('not.exist');
        });

        it('shows the Download ZIM button disabled', () => {
          cy.get('#download').should('be.visible');
          cy.get('#download').should('have.attr', 'disabled');
        });

        it('shows the spinner', () => {
          cy.get('#loader').should('be.visible');
        });
      });

      describe('when the zim file is ready', () => {
        beforeEach(() => {
          cy.intercept('v1/builders/1/zim/status', {
            fixture: 'zim_status_ready.json',
          }).as('status');
          cy.visit('/#/selections/1/zim');
          cy.wait('@identity');
          cy.wait('@builder');
          cy.wait('@status');
        });

        it('does not display the form for descriptions', () => {
          cy.get('#desc').should('not.exist');
          cy.get('#longdesc').should('not.exist');
        });

        it('shows the Download ZIM button enabled', () => {
          cy.get('#download').should('be.visible');
          cy.get('#download').should('not.have.attr', 'disabled');
        });

        it('does not show the spinner', () => {
          cy.get('#loader').should('not.be.visible');
        });
      });

      describe('when the zim file has failed', () => {
        beforeEach(() => {
          cy.intercept('v1/builders/1/zim/status', {
            fixture: 'zim_status_failed.json',
          }).as('status');
          cy.visit('/#/selections/1/zim');
          cy.wait('@identity');
          cy.wait('@builder');
          cy.wait('@status');
        });

        it('displays the form for entering descriptions', () => {
          cy.get('#desc').should('be.visible');
          cy.get('#longdesc').should('be.visible');
        });

        it('does not show the spinner', () => {
          cy.get('#loader').should('not.be.visible');
        });

        it('displays the Request ZIM file button', () => {
          cy.get('#request').should('be.visible');
          cy.get('#request').should('not.have.attr', 'disabled');
        });

        describe('when the Request ZIM file button is clicked', () => {
          beforeEach(() => {
            cy.intercept('POST', 'v1/builders/1/zim', {
              statusCode: 204,
            }).as('request');

            cy.get('#desc').click();
            cy.get('#desc').type('Description from user');
            cy.get('#request').click();
          });

          it('makes the ZIM file request', () => {
            cy.wait('@request');
          });
        });
      });

      describe('when the zim file is expired', () => {
        beforeEach(() => {
          cy.intercept('v1/builders/1/zim/status', {
            fixture: 'zim_status_deleted.json',
          }).as('status');
          cy.visit('/#/selections/1/zim');
          cy.wait('@identity');
          cy.wait('@builder');
          cy.wait('@status');
        });

        it('displays the form for entering descriptions', () => {
          cy.get('#desc').should('be.visible');
          cy.get('#longdesc').should('be.visible');
        });

        it('does not show the spinner', () => {
          cy.get('#loader').should('not.be.visible');
        });

        it('displays the Request ZIM file button', () => {
          cy.get('#request').should('be.visible');
          cy.get('#request').should('not.have.attr', 'disabled');
        });
      });
    });

    describe('and the builder is not found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          statusCode: 404,
          body: '404 NOT FOUND',
        });
        cy.visit('/#/selections/1/zim');
      });

      it('displays the 404 text', () => {
        cy.get('#404').should('be.visible');
      });
    });
  });
});
