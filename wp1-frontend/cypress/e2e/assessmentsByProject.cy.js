/// <reference types="Cypress" />

describe('the assessments by project page', () => {
  beforeEach(() => {
    cy.intercept('v1/projects/assessments', { fixture: 'assessments.json' });
  });

  it('is reachable from the nav bar', () => {
    cy.visit('/');
    cy.get('header nav').contains('a', 'Assessments by Project').click();
    cy.url().should('include', '/assessments');
  });

  it('lists the assessment numbers in a table', () => {
    cy.visit('/#/assessments');

    cy.get('table').find('thead th').eq(0).should('contain.text', 'Project');
    cy.get('table').find('thead th').eq(1).should('contain.text', 'Unassessed');
    cy.get('table').find('thead th').eq(2).should('contain.text', 'Assessed');

    // Rows default-sort by unassessed descending, matching the API order.
    cy.get('table thead th')
      .eq(1)
      .should('have.attr', 'aria-sort', 'descending');
    cy.get('table tbody tr').should('have.length', 3);

    cy.get('table tbody tr')
      .eq(0)
      .within(() => {
        cy.get('td').eq(0).should('contain.text', 'Primate');
        cy.get('td').eq(1).should('contain.text', '349');
        cy.get('td').eq(2).should('contain.text', '1,594');
      });

    // Underscores in project names are displayed as spaces.
    cy.get('table tbody tr')
      .eq(1)
      .find('td')
      .eq(0)
      .should('contain.text', 'WikiProject East Timor');

    cy.contains('1 – 3 of 3');
  });

  it('sorts by column on header click', () => {
    cy.visit('/#/assessments');

    // Toggling the active Unassessed column flips it to ascending.
    cy.get('table thead th').eq(1).find('button').click();
    cy.get('table thead th')
      .eq(1)
      .should('have.attr', 'aria-sort', 'ascending');
    cy.get('table tbody tr').eq(0).should('contain.text', 'Water');

    // Sorting by project name goes alphabetical.
    cy.get('table thead th').eq(0).find('button').click();
    cy.get('table thead th')
      .eq(0)
      .should('have.attr', 'aria-sort', 'ascending');
    cy.get('table tbody tr').eq(0).should('contain.text', 'Primate');
    cy.get('table tbody tr').eq(1).should('contain.text', 'Water');
  });

  it('filters rows via the search box', () => {
    cy.visit('/#/assessments');

    cy.get('input[aria-label="Filter projects"]').type('Water');

    cy.get('table tbody tr').should('have.length', 1);
    cy.get('table tbody tr').eq(0).should('contain.text', 'Water');
  });

  it('focuses the search box on "/"', () => {
    cy.visit('/#/assessments');

    cy.get('table tbody tr').should('have.length', 3);
    cy.get('body').type('/');
    cy.get('input[aria-label="Filter projects"]').should('be.focused');
  });

  it('links each project to its project page', () => {
    cy.visit('/#/assessments');

    cy.get('table tbody tr').contains('a', 'Water').click();
    cy.url().should('include', '/project/Water');
  });
});
