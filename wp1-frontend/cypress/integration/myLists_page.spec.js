/// <reference types="Cypress" />

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
    const listTd = cy.contains('td', 'list_name');
    listTd.siblings().contains('td', 'en.wikipedia.org');
    listTd.siblings().contains('td', '9/5/2021');
    listTd.siblings().contains('.btn-primary', 'Edit');
  });

  it('displays "-" for updated and download of list with no selection', () => {
    const listTd = cy.contains('td', 'list 2');
    listTd.parent('tr').within(td => {
      cy.get('td')
        .eq(4)
        .contains('-');
      cy.get('td')
        .eq(5)
        .contains('-');
    });
  });

  it('takes the user to the edit screen when edit is clicked', () => {
    cy.intercept('GET', 'v1/builders/1', { fixture: 'builder_1.json' });
    cy.contains('td', 'list_name')
      .siblings()
      .contains('.btn-primary', 'Edit')
      .click();
    cy.url().should('eq', 'http://localhost:3000/#/selections/simple/1');
  });
});

describe('when the user is not logged in', () => {
  it('opens login page', () => {
    cy.visit('/#/selections/user');
    cy.contains('Please Log In To Continue');
    cy.get('.pt-2 > .btn');
  });
});
