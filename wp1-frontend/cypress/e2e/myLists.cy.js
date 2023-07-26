/// <reference types="Cypress" />

describe('the user selection list page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/selection/simple/lists', {
        fixture: 'list_data.json',
      }).as('list');
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
      cy.visit('/#/selections/user');
      cy.get('select').select('25');
    });

    it('successfully loads', () => {});

    it('displays the datatables view', () => {
      cy.get('.dataTables_info').contains('Showing 1 to 12 of 12 entries');
    });

    it('displays list and its contents', () => {
      const listTd = cy.contains('td', 'simple list');
      listTd.siblings().contains('td', 'en.wikipedia.org');
      listTd.siblings().contains('td', '9/5/21');
      listTd.siblings().contains('.btn-primary', 'Edit');
    });

    it('displays a spinner for download of list with no selection', () => {
      const listTd = cy.contains('td', 'sparql list');
      listTd.parent('tr').within(() => {
        cy.get('td').eq(4).contains('-');
        cy.get('td').eq(5).get('div').should('have.class', 'loader');
      });
    });

    it('displays a spinner if the selection is newer than the builder', () => {
      cy.contains('td', 'updated list')
        .parent('tr')
        .within(() => {
          cy.get('td').eq(5).get('div').should('have.class', 'loader');
        });
    });

    it('displays a spinner if the selection has error and is retrying', () => {
      cy.contains('td', 'in retry')
        .parent('tr')
        .within(() => {
          cy.get('td').eq(5).get('div').should('have.class', 'loader');
        });
    });

    it('displays error message for list with permanent error', () => {
      cy.contains('td', 'permanent error')
        .parent('tr')
        .within(() => {
          cy.get('td').eq(5).get('div').should('contain', 'FAILED');
        });
    });

    it('displays error message for list with retryable failure', () => {
      cy.contains('td', 'retryable error')
        .parent('tr')
        .within(() => {
          cy.get('td').eq(5).get('div').should('contain', 'FAILED');
        });
    });

    it('takes the user to the simple edit screen when simple edit is clicked', () => {
      cy.intercept('GET', 'v1/builders/1', { fixture: 'simple_builder.json' });
      cy.contains('td', 'simple list')
        .siblings()
        .contains('.btn-primary', 'Edit')
        .click();
      cy.url().should('eq', 'http://localhost:5173/#/selections/simple/1');
    });

    it('takes the user to the SPARQL edit screen when SPARQL edit is clicked', () => {
      cy.intercept('GET', 'v1/builders/1', { fixture: 'sparql_builder.json' });
      cy.contains('td', 'sparql list')
        .siblings()
        .contains('.btn-primary', 'Edit')
        .click();
      cy.url().should('eq', 'http://localhost:5173/#/selections/sparql/2');
    });

    it('displays a failed link for selection with failed ZIM', () => {
      cy.contains('td', 'zim failed')
        .parent('tr')
        .within(() => {
          cy.get('td').eq(7).get('span').should('contain', 'Failed');
        });
    });

    it('goes to the zim page when the failed link is clicked', () => {
      cy.contains('td', 'zim failed')
        .parent('tr')
        .within(() => {
          cy.get('td').eq(7).get('span a').click();
        });
      cy.url().should('eq', 'http://localhost:5173/#/selections/3a3d4c8e/zim');
    });

    describe('when the selection has not been materialized', () => {
      it('does not display the Create Zim button', () => {
        cy.contains('td', 'in retry')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).should('contain', '-');
          });
      });

      it('does not display the ZIM updated date', () => {
        cy.contains('td', 'in retry')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(6).should('contain', '-');
          });
      });
    });

    describe('when the selection is materialized', () => {
      it('displays the Create Zim button', () => {
        cy.contains('td', 'selection ready, no zim')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).should('contain', 'Create ZIM');
          });
      });

      it('does not display the ZIM updated date', () => {
        cy.contains('td', 'selection ready, no zim')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(6).should('contain', '-');
          });
      });
    });

    describe('when the ZIM file has been requested but is not yet ready', () => {
      it('displays a spinner', () => {
        cy.contains('td', 'zim requested')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).get('div').should('have.class', 'loader');
          });
      });

      it('does not display the ZIM updated date', () => {
        cy.contains('td', 'zim requested')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(6).should('contain', '-');
          });
      });
    });

    describe('when the ZIM file is ready', () => {
      beforeEach(() => {
        cy.clock(1685991600000);
        cy.visit('/#/selections/user');
        cy.wait('@list')
          .then(cy.clock)
          .then((clock) => {
            console.log('restoring');
            clock.restore();
          });
      });

      it('displays the download ZIM link', () => {
        cy.contains('td', 'zim ready')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).get('a').should('contain', 'Download ZIM');
          });
      });

      it('displays the ZIM updated date', () => {
        cy.contains('td', 'zim ready')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(6).should('contain', '6/1/23');
          });
      });
    });

    describe('when there is an outdated ZIM', () => {
      it('displays the download ZIM link', () => {
        cy.contains('td', 'outdated zim')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).get('a').should('contain', 'Download ZIM');
          });
      });

      it('displays the ZIM updated date', () => {
        cy.contains('td', 'outdated zim')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(6).should('contain', '6/1/23');
          });
      });

      it('shows the info hover', () => {
        cy.contains('td', 'outdated zim')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).get('span').should('exist');
          });
      });
    });

    describe('when there is an deleted ZIM', () => {
      it('displays the ZIM updated date', () => {
        cy.contains('td', 'deleted zim')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(6).should('contain', '6/18/23');
          });
      });

      it('displays the Create Zim button', () => {
        cy.contains('td', 'deleted zim')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).should('contain', 'Create ZIM');
          });
      });

      it('shows the info hover', () => {
        cy.contains('td', 'deleted zim')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).get('span').should('exist');
          });
      });
    });

    describe('when there is a failed ZIM', () => {
      it('does not display the ZIM updated date', () => {
        cy.contains('td', 'zim failed')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(6).should('contain', '-');
          });
      });

      it('displays a link to the zim creation page', () => {
        cy.contains('td', 'zim failed')
          .parent('tr')
          .within(() => {
            cy.get('td').eq(7).should('contain', 'Failed');
          });
      });
    });
  });

  describe('when the user is not logged in', () => {
    it('opens login page', () => {
      cy.visit('/#/selections/user');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
