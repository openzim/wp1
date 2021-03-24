/// <reference types="Cypress" />

describe('the project page', () => {
    it('displays row and column labels in project-table', () => {
        cy.visit('/#/project/Aesthetics');
        
        const col_labels = ['Top','High','Mid','Low','NA','???'];
        col_labels.forEach(label => {
            cy.get('table').contains('th', label);
        });

        const row_labels = ['GA','B','C','Start','Stub','List','Category','Disambig','File','Project','Redirect','Template','Other','Assessed'];
        row_labels.forEach(label => {
            cy.get('table').contains('tr', label);
        });
    });
});