/// <reference types="Cypress" />

describe('the project page', () => {
  it('displays row and column labels in project-table', () => {
    cy.visit('/#/project/Aesthetics');

    const col_labels = ['Top', 'High', 'Mid', 'Low', 'NA', '???'];
    col_labels.forEach((label) => {
      cy.get('table').contains('th', label);
    });

    const row_labels = [
      'GA',
      'B',
      'C',
      'Start',
      'Stub',
      'List',
      'Category',
      'Disambig',
      'File',
      'Project',
      'Redirect',
      'Template',
      'Other',
      'Assessed',
    ];
    row_labels.forEach((label) => {
      cy.get('table').contains('tr', label);
    });
  });

  it('displays the article detail-list', () => {
    cy.visit('/#/project/Alien');

    cy.get('tr')
      .eq(3)
      .find('td')
      .eq(0)
      .invoke('text')
      .then((text) => {
        cy.get('tr').eq(3).find('td').eq(0).contains(/^\d+$/).click();
        cy.get('tr').should('have.length', text);
      });

    cy.get('h4').should(
      'contain.text',
      ' Alien articles  - Top importance / FA quality'
    );

    cy.get('tr')
      .eq(0)
      .find('td')
      .then(($row) => {
        cy.wrap($row).eq(2).contains('Top');
        cy.wrap($row).eq(4).contains('FA');
      });
  });
});
