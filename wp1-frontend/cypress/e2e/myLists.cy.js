/// <reference types="Cypress" />

describe('the user selection list page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/selection/simple/lists', { fixture: 'list_data.json' });
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
      cy.visit('/#/selections/user');
    });

    it('successfully loads', () => {});

    it('displays the datatables view', () => {
      cy.get('.dataTables_info').contains('Showing 1 to 2 of 2 entries');
    });

    it('displays list and its contents', () => {
      const listTd = cy.contains('td', 'simple list');
      listTd.siblings().contains('td', 'en.wikipedia.org');
      listTd.siblings().contains('td', '9/5/2021');
      listTd.siblings().contains('.btn-primary', 'Edit');
    });

    it('displays a spinner for download of list with no selection', () => {
      const listTd = cy.contains('td', 'sparql list');
      listTd.parent('tr').within((td) => {
        cy.get('td').eq(4).contains('-');
        cy.get('td').eq(5).get('div').should('have.class', 'loader');
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
  });

  describe('when the user is not logged in', () => {
    it('opens login page', () => {
      cy.visit('/#/selections/user');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
