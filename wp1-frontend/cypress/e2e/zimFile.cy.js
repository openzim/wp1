/// <reference types="Cypress" />

describe('the zim file creation page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'identity',
      );
    });

    describe('and the builder is found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          fixture: 'simple_builder.json',
        }).as('builder');
      });

      describe('and the selection is under the article limit', () => {
        beforeEach(() => {
          cy.intercept('GET', 'v1/builders/1/selection/latest/article_count', {
            selection: {
              id: '1',
              aricle_count: 1000,
              max_article_count: 50000,
            },
          }).as('article_count');
        });

        describe('when the zim file has not been requested yet', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_not_requested.json',
            }).as('status');
            cy.intercept('POST', 'v1/builders/1/zim', { statusCode: 204 }).as(
              'create',
            );
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('displays the form for entering descriptions', () => {
            cy.get('#desc').should('be.visible');
            cy.get('#longdesc').should('be.visible');
          });

          it('validates the title input on losing focus', () => {
            cy.get('#zimtitle').click();
            cy.get('#zimtitle').clear();
            cy.get('#longdesc').click();
            cy.get('#zimtitle-group > .invalid-feedback').should('be.visible');
          });

          it('validates the title input to have max 30 graphemes', () => {
            const longTitle = 'A'.repeat(31);
            cy.get('#zimtitle').click();
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type(longTitle);
            cy.get('#zimtitle').should(
              'have.value',
              longTitle.substring(0, 30),
            );
          });

          it('handles graphemes correctly', () => {
            const longTitle = 'में'.repeat(30);
            cy.get('#zimtitle').click();
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type(longTitle);
            cy.get('#zimtitle').should('have.value', 'में'.repeat(30));
          });

          it('does not show the long description invalid feedback if it is empty', () => {
            cy.get('#desc').click();
            cy.get('#longdesc').click();
            cy.get('#long-desc-group > .invalid-feedback').should(
              'not.be.visible',
            );
          });

          it('does not allow submission if the long desc is shorter than the desc', () => {
            cy.get('#zimtitle').click();
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type('Title from user');
            cy.get('#desc').click();
            cy.get('#desc').clear();
            cy.get('#desc').type('The description, which is longer');
            cy.get('#longdesc').click();
            cy.get('#longdesc').type('Shorter desc');
            cy.get('#request').click();
            cy.get('#long-desc-group > .invalid-feedback').should('be.visible');
            cy.wait(400);
            cy.get('@create.all').then((interceptions) => {
              expect(interceptions).to.have.length(0);
            });
          });

          it('does not allow submission if the long desc equals the desc', () => {
            cy.get('#zimtitle').click();
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type('Title from user');
            cy.get('#desc').click();
            cy.get('#desc').clear();
            cy.get('#desc').type('The description');
            cy.get('#longdesc').click();
            cy.get('#longdesc').type('The description');
            cy.get('#request').click();
            cy.get('#long-desc-group > .invalid-feedback').should('be.visible');
            cy.wait(400);
            cy.get('@create.all').then((interceptions) => {
              expect(interceptions).to.have.length(0);
            });
          });

          it('allows submission if the long desc is empty', () => {
            cy.get('#zimtitle').click();
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type('Title from user');
            cy.get('#desc').click();
            cy.get('#desc').clear();
            cy.get('#desc').type('The description');
            cy.get('#longdesc').click();
            cy.get('#longdesc').clear();
            cy.get('#request').click();
            cy.wait('@create');
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
            cy.get('#zimtitle').click();
            cy.get('#zimtitle').type('Title from user');
            cy.get('#desc').click();
            cy.get('#desc').type('Description from user');
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
            cy.get('#zimtitle').click();
            cy.get('#zimtitle').type('Title from user');
            cy.get('#desc').click();
            cy.get('#desc').type('Description from user');
            cy.get('#request').should('be.visible');
            cy.get('#request').should('not.have.attr', 'disabled');
          });
        });
      });

      describe('and the selection is over the article limit', () => {
        beforeEach(() => {
          cy.intercept('GET', 'v1/builders/1/selection/latest/article_count', {
            selection: {
              id: '1',
              article_count: 100000,
              max_article_count: 50000,
            },
          }).as('article_count');
          cy.intercept('v1/builders/1/zim/status', {
            fixture: 'zim_status_not_requested.json',
          }).as('status');
        });

        it('displays the article error message', () => {
          cy.visit('/#/selections/1/zim');
          cy.wait('@identity');
          cy.wait('@builder');
          cy.wait('@status');
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
