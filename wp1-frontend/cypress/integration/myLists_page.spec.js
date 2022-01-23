/// <reference types="Cypress" />

describe('when the user is logged in', () => {
  beforeEach(() => {
    cy.intercept('v1/selection/simple/lists', { fixture: 'list_data.json' });
    cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
    cy.visit('/#/selections/user');
  });

  it('successfully loads', () => {});

  it('displays the datatables view', () => {
    cy.get('.dataTables_info').contains('Showing 1 to 1 of 1 entries');
  });

  it('displays list and its contents', () => {
    cy.get('#list-table td').contains('list_name');
    cy.get('#list-table td').contains('en.wikipedia.org');
    cy.get('#list-table td').contains('9/5/2021 2:28:23 PM');
    cy.get('#list-table td').contains('9/5/2021 2:45:03 PM');
    cy.get('#list-table td').contains('9/5/2021 3:18:23 PM');
    cy.get('#list-table td .btn-primary').contains('Edit');
  });

  it('takes the user to the edit screen when edit is clicked', () => {
    cy.intercept('GET', 'v1/builders/1', { fixture: 'builder_1.json' });
    cy.get('#list-table td .btn-primary').click();
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
