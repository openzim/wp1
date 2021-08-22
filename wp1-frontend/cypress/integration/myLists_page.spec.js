/// <reference types="Cypress" />

describe('when the user is logged in', () => {
  beforeEach(() => {
    cy.intercept('v1/selection/simple/lists', { fixture: 'list_data.json' });
    cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
  });

  it('successfully loads', () => {
    cy.visit('/#/selections/user');
  });

  it('displays list and its contents', () => {
    cy.get('.row').contains('list_name');
    cy.get('.row').contains('en.wikipedia.org');
    cy.get('.btn-primary').contains('Download tsv');
  });

  it('copy button works', () => {
    cy.get('.input-group-append > .btn')
      .contains('Copy')
      .click();
    cy.get('#1')
      .invoke('val')
      .should(val => expect(val).to.eql('https://www.example.com/<id>'));
  });
});

describe('when the user is not logged in', () => {
  it('opens login page', () => {
    cy.visit('/#/selections/user');
    cy.contains('Please Log In To Continue');
    cy.get('.pt-2 > .btn');
  });
});
