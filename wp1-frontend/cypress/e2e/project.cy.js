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
      'Alien articles  - Top importance / FA quality'
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
