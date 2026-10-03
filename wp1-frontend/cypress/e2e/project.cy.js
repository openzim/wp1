/// <reference types="Cypress" />

describe('the project page', () => {
  beforeEach(() => {
    cy.intercept('v1/projects/Aesthetics', {
      fixture: 'project_aesthetics.json',
    });
    cy.intercept('v1/projects/Aesthetics/table', {
      fixture: 'project_table_aesthetics.json',
    });
    cy.intercept('v1/projects/Alien', { fixture: 'project_alien.json' });
    cy.intercept('v1/projects/Alien/table', {
      fixture: 'project_table_alien.json',
    });
    cy.intercept(
      {
        pathname: '/v1/projects/Alien/articles',
        query: { importance: 'Top-Class', quality: 'FA-Class' },
      },
      { fixture: 'articles_alien_top_fa.json' }
    );
  });

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

    // The FA row's first count cell is the Top-Class importance column.
    cy.get('table')
      .contains('th', 'FA')
      .parent('tr')
      .find('td')
      .first()
      .invoke('text')
      .then((text) => {
        const count = Number(text.replace(/,/g, ''));
        cy.get('table')
          .contains('th', 'FA')
          .parent('tr')
          .find('td')
          .first()
          .find('a')
          .click();
        cy.get('tbody tr').should('have.length', count);
      });

    cy.contains('h2', 'Alien articles');
    cy.contains('a', 'Top importance');
    cy.contains('a', 'FA quality');

    cy.get('tbody tr')
      .eq(0)
      .find('td')
      .then(($row) => {
        cy.wrap($row).eq(3).contains('Top');
        cy.wrap($row).eq(5).contains('FA');
      });
  });
});
