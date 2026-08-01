/// <reference types="Cypress" />

describe('the manual update page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
    });

    describe('and no project is selected', () => {
      beforeEach(() => {
        cy.visit('/#/update');
      });

      it('successfully loads', () => {});

      it('displays the manual update instructions', () => {
        cy.contains('To begin a manual update');
      });

      it('does not show the update button', () => {
        cy.contains('button', 'Manual Update').should('not.exist');
      });
    });

    describe('and a project is selected via autocomplete', () => {
      beforeEach(() => {
        cy.intercept('v1/projects/Alien/update/time', {
          body: { next_update_time: null },
        }).as('updateTime');
        cy.visit('/#/update');
        cy.get('input.search').type('Alien');
        cy.get('.results .result').first().click();
        cy.wait('@updateTime');
      });

      it('navigates to the project update URL', () => {
        cy.url().should('eq', 'http://localhost:5173/#/update/Alien');
      });

      it('shows the update confirmation button', () => {
        cy.contains('Proceed with manual update of');
        cy.contains('button', 'Manual Update');
      });

      describe('when the update button is clicked', () => {
        beforeEach(() => {
          cy.intercept('POST', 'v1/projects/Alien/update', {
            body: { next_update_time: '2026-08-01T00:00:00Z' },
          }).as('postUpdate');
          cy.intercept('v1/projects/Alien/update/progress', {
            body: {
              job: { progress: 50, total: 100 },
              queue: { status: 'started' },
            },
          }).as('progress');
          cy.contains('button', 'Manual Update').click();
        });

        it('POSTs to the update endpoint', () => {
          cy.wait('@postUpdate');
        });

        it('shows the scheduled message and progress bar', () => {
          cy.wait('@progress');
          cy.contains('has been scheduled');
          cy.get('.progress-bar').should('be.visible');
        });
      });
    });

    describe('and the project is provided in the URL', () => {
      beforeEach(() => {
        cy.intercept('v1/projects/Alien/update/time', {
          body: { next_update_time: '2026-08-01T00:00:00Z' },
        }).as('updateTime');
        cy.intercept('v1/projects/Alien/update/progress', {
          body: { job: null, queue: { status: 'queued' } },
        }).as('progress');
        cy.visit('/#/update/Alien');
        cy.wait('@updateTime');
      });

      it('prefills the autocomplete from the URL', () => {
        cy.get('input.search').should('have.value', 'Alien');
      });

      it('shows the next update time instead of the button', () => {
        cy.contains('has been scheduled');
        cy.contains('2026-08-01T00:00:00Z');
        cy.contains('button', 'Manual Update').should('not.exist');
      });

      it('shows the scheduled-but-not-started progress string', () => {
        cy.wait('@progress');
        cy.contains("hasn't started yet");
      });
    });
  });

  describe('when the user is not logged in', () => {
    it('shows the login required page', () => {
      cy.visit('/#/update');
      cy.contains('Please Log In To Continue');
      cy.get('.pt-2 > .btn');
    });
  });
});
