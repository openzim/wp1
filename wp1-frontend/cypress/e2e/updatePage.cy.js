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

      it('displays the manual update rate-limit note', () => {
        cy.contains('once per hour at most');
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
        cy.url().should('eq', `${Cypress.config('baseUrl')}/#/update/Alien`);
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
          cy.get('[role="progressbar"]').should('be.visible');
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

    describe('and a project with spaces in its name is selected', () => {
      beforeEach(() => {
        cy.intercept('v1/projects/Bob_Dylan/update/time', {
          body: { next_update_time: null },
        }).as('updateTime');
        cy.visit('/#/update');
        cy.get('input.search').type('Bob Dylan');
        cy.get('.results .result').first().click();
      });

      it('requests the update time with underscores in the project id', () => {
        cy.wait('@updateTime');
      });

      it('navigates to the project update URL', () => {
        cy.url().should(
          'eq',
          `${Cypress.config('baseUrl')}/#/update/Bob%20Dylan`
        );
      });

      describe('when the update button is clicked', () => {
        it('POSTs to the underscored update endpoint', () => {
          cy.wait('@updateTime');
          cy.intercept('POST', 'v1/projects/Bob_Dylan/update', {
            body: { next_update_time: '2026-08-01T00:00:00Z' },
          }).as('postUpdate');
          cy.intercept('v1/projects/Bob_Dylan/update/progress', {
            body: { job: null, queue: { status: 'queued' } },
          });
          cy.contains('button', 'Manual Update').click();
          cy.wait('@postUpdate');
        });
      });
    });

    describe('and the update job is running', () => {
      beforeEach(() => {
        cy.intercept('v1/projects/Alien/update/time', {
          body: { next_update_time: '2026-08-01T00:00:00Z' },
        }).as('updateTime');
        cy.intercept('v1/projects/Alien/update/progress', {
          body: {
            job: { progress: 50, total: 100 },
            queue: { status: 'started' },
          },
        }).as('progress');
        cy.visit('/#/update/Alien');
        cy.wait('@progress');
      });

      it('shows the running progress string', () => {
        cy.contains('Your job is running, track its progress below.');
      });

      it('shows the article counts', () => {
        cy.contains('50 / 100 articles');
      });

      it('shows a progress bar with the job progress values', () => {
        cy.get('[role="progressbar"]')
          .should('have.attr', 'aria-valuenow', '50')
          .should('have.attr', 'aria-valuemax', '100');
      });
    });

    describe('and the update job is finishing up', () => {
      beforeEach(() => {
        cy.intercept('v1/projects/Alien/update/time', {
          body: { next_update_time: '2026-08-01T00:00:00Z' },
        }).as('updateTime');
        cy.intercept('v1/projects/Alien/update/progress', {
          body: {
            job: { progress: 100, total: 100 },
            queue: { status: 'started' },
          },
        }).as('progress');
        cy.visit('/#/update/Alien');
        cy.wait('@progress');
      });

      it('shows the finishing-up progress string', () => {
        cy.contains(
          'Your job is almost finished, just wrapping up some tasks.'
        );
      });
    });

    describe('and the update job is complete', () => {
      beforeEach(() => {
        cy.intercept('v1/projects/Alien/update/time', {
          body: { next_update_time: '2026-08-01T00:00:00Z' },
        }).as('updateTime');
        cy.intercept('v1/projects/Alien/update/progress', {
          body: { job: null, queue: { status: 'finished' } },
        }).as('progress');
        cy.visit('/#/update/Alien');
        cy.wait('@progress');
      });

      it('shows the complete progress string', () => {
        cy.contains('Your job is complete!');
      });

      it('hides the progress bar', () => {
        cy.contains('Your job is complete!');
        cy.get('[role="progressbar"]').should('not.exist');
      });

      it('stops polling for progress', () => {
        // Polling runs every 2 seconds; after the job reports finished, no
        // further progress requests should be made.
        cy.contains('Your job is complete!');
        cy.wait(2500);
        cy.get('@progress.all').should('have.length', 1);
      });
    });
  });

  describe('when the user is not logged in', () => {
    it('shows the login required page', () => {
      cy.visit('/#/update');
      cy.contains('Sign in required');
      cy.contains('a', 'Sign in with Wikipedia');
    });
  });
});
