/// <reference types="Cypress" />

describe('the zim file creation page', () => {
  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'identity'
      );
    });

    describe('and the builder is found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          fixture: 'simple_builder.json',
        }).as('builder');
      });

      describe('and the article count fetch fails', () => {
        it('shows the server error page with the HTTP status', () => {
          cy.intercept('GET', 'v1/builders/1/selection/latest/article_count', {
            statusCode: 502,
            body: {},
          }).as('article_count_fail');
          cy.intercept('v1/builders/1/zim/status', {
            fixture: 'zim_status_not_requested.json',
          }).as('status');
          cy.visit('/#/selections/1/zim');
          cy.wait('@article_count_fail');
          cy.contains('Server error');
          cy.get('#error-http-status').contains(
            'The server responded with HTTP 502.'
          );
        });
      });

      describe('and the zim status fetch fails', () => {
        it('surfaces the HTTP status in the error list', () => {
          cy.intercept('GET', 'v1/builders/1/selection/latest/article_count', {
            selection: {
              id: '1',
              article_count: 1000,
              max_article_count: 50000,
            },
          }).as('article_count');
          cy.intercept('v1/builders/1/zim/status', {
            statusCode: 503,
            body: {},
          }).as('status_fail');
          cy.visit('/#/selections/1/zim');
          cy.wait('@status_fail');
          cy.contains('The ZIM status could not be loaded (HTTP 503).');
        });
      });

      describe('and the selection is under the article limit', () => {
        beforeEach(() => {
          cy.intercept('GET', 'v1/builders/1/selection/latest/article_count', {
            selection: {
              id: '1',
              article_count: 1000,
              max_article_count: 50000,
            },
          }).as('article_count');
        });

        describe('when the zim file has not been requested yet', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_not_requested.json',
            }).as('status');
            cy.intercept('POST', 'v1/builders/1/zim', { statusCode: 204 }).as(
              'create'
            );
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('displays the form for entering descriptions', () => {
            cy.get('#desc').should('be.visible');
            cy.get('#longdesc').should('be.visible');
          });

          it('pre-fills the title from the builder name', () => {
            cy.get('#zimtitle').should('have.value', 'Builder 1');
          });

          it('links back to the selection detail pane', () => {
            cy.contains('a', 'Builder 1').should(
              'have.attr',
              'href',
              '#/selections/user/1'
            );
          });

          it('requires a title on submit', () => {
            cy.get('#zimtitle').clear();
            cy.get('#desc').type('The description');
            cy.get('#request').click();
            cy.contains('Please provide a title');
            cy.wait(400);
            cy.get('@create.all').then((interceptions) => {
              expect(interceptions).to.have.length(0);
            });
          });

          it('validates the title input to have max 30 graphemes', () => {
            const longTitle = 'A'.repeat(31);
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type(longTitle);
            cy.get('#zimtitle').should(
              'have.value',
              longTitle.substring(0, 30)
            );
          });

          it('handles graphemes correctly', () => {
            const longTitle = 'में'.repeat(30);
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type(longTitle);
            cy.get('#zimtitle').should('have.value', 'में'.repeat(30));
          });

          it('does not show long description feedback when it is empty', () => {
            cy.get('#desc').click();
            cy.get('#longdesc').click();
            cy.contains(
              'Long description must differ from description and not be shorter'
            ).should('not.exist');
          });

          it('does not allow submission if the long desc is shorter than the desc', () => {
            cy.get('#desc').type('The description, which is longer');
            cy.get('#longdesc').type('Shorter desc');
            cy.get('#request').click();
            cy.contains(
              'Long description must differ from description and not be shorter'
            ).should('be.visible');
            cy.wait(400);
            cy.get('@create.all').then((interceptions) => {
              expect(interceptions).to.have.length(0);
            });
          });

          it('does not allow submission if the long desc equals the desc', () => {
            cy.get('#desc').type('The description');
            cy.get('#longdesc').type('The description');
            cy.get('#request').click();
            cy.contains(
              'Long description must differ from description and not be shorter'
            ).should('be.visible');
            cy.wait(400);
            cy.get('@create.all').then((interceptions) => {
              expect(interceptions).to.have.length(0);
            });
          });

          it('allows submission if the long desc is empty', () => {
            cy.get('#desc').type('The description');
            cy.get('#request').click();
            cy.wait('@create');
          });
        });

        describe('when the zim file has been requested but is not ready', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_not_ready.json',
            }).as('status');
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('does not display the form for descriptions', () => {
            cy.get('#desc').should('not.exist');
            cy.get('#longdesc').should('not.exist');
          });

          it('shows the Download ZIM button disabled', () => {
            cy.get('#download').should('be.visible');
            cy.get('#download').should('have.attr', 'disabled');
          });

          it('shows the building indicator', () => {
            cy.contains('Building…').should('be.visible');
          });
        });

        describe('when the zim file is ready', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_ready.json',
            }).as('status');
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('does not display the form for descriptions', () => {
            cy.get('#desc').should('not.exist');
            cy.get('#longdesc').should('not.exist');
          });

          it('shows the Download ZIM button enabled', () => {
            cy.get('#download').should('be.visible');
            cy.get('#download').should('not.have.attr', 'disabled');
          });

          it('does not show the building indicator', () => {
            cy.contains('Building…').should('not.exist');
          });
        });

        describe('when the zim file has failed', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_failed.json',
            }).as('status');
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('displays the form for entering descriptions', () => {
            cy.get('#desc').should('be.visible');
            cy.get('#longdesc').should('be.visible');
          });

          it('displays the error message with the zimfarm link', () => {
            cy.contains('There was an error creating your ZIM file');
            cy.contains('a', 'via the Zimfarm API').should(
              'have.attr',
              'href',
              'https://example.fake/failed'
            );
          });

          describe('when the Request ZIM file button is clicked', () => {
            beforeEach(() => {
              cy.intercept('POST', 'v1/builders/1/zim', {
                statusCode: 204,
              }).as('request');

              cy.get('#desc').type('Description from user');
              cy.get('#request').click();
            });

            it('makes the ZIM file request', () => {
              cy.wait('@request');
            });
          });
        });

        describe('when the zim file is expired', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_deleted.json',
            }).as('status');
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('displays the expired message and the request form', () => {
            cy.contains('Your ZIM file has expired');
            cy.get('#desc').should('be.visible');
            cy.get('#longdesc').should('be.visible');
            cy.get('#request').should('be.visible');
          });
        });

        describe('scheduling form UI', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_not_requested.json',
            }).as('status');
            cy.intercept('GET', 'v1/oauth/email', {
              body: { email: 'test@example.org' },
            }).as('email');
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('shows the scheduling checkbox unchecked by default', () => {
            cy.get('#enableScheduling').should('be.visible');
            cy.get('#enableScheduling').should('not.be.checked');
          });

          it('does not show scheduling options when checkbox is unchecked', () => {
            cy.get('#repetitionPeriod').should('not.exist');
            cy.get('#numberOfRepetitions').should('not.exist');
            cy.get('#scheduleEmail').should('not.exist');
          });

          it('shows scheduling options when checkbox is checked', () => {
            cy.get('#enableScheduling').check();
            cy.get('#repetitionPeriod').should('be.visible');
            cy.get('#numberOfRepetitions').should('be.visible');
            cy.get('#scheduleEmail').should('be.visible');
          });

          it('shows the correct period options (1, 3, 6)', () => {
            cy.get('#enableScheduling').check();
            cy.get('#repetitionPeriod option').should('have.length', 3);
            cy.get('#repetitionPeriod option').eq(0).should('have.value', '1');
            cy.get('#repetitionPeriod option').eq(1).should('have.value', '3');
            cy.get('#repetitionPeriod option').eq(2).should('have.value', '6');
          });

          it('shows the correct repetition options (1, 2, 3)', () => {
            cy.get('#enableScheduling').check();
            cy.get('#numberOfRepetitions option').should('have.length', 3);
            cy.get('#numberOfRepetitions option')
              .eq(0)
              .should('have.value', '1');
            cy.get('#numberOfRepetitions option')
              .eq(1)
              .should('have.value', '2');
            cy.get('#numberOfRepetitions option')
              .eq(2)
              .should('have.value', '3');
          });

          it('pre-fills the schedule email from the user email endpoint', () => {
            cy.get('#enableScheduling').check();
            cy.get('#scheduleEmail').should('have.value', 'test@example.org');
          });
        });

        describe('submitting with scheduling enabled', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_not_requested.json',
            }).as('status');
            cy.intercept('GET', 'v1/oauth/email', {
              body: { email: '' },
            }).as('email');
            cy.intercept('POST', 'v1/builders/1/zim', { statusCode: 204 }).as(
              'create'
            );
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('includes scheduled_repetitions in the request body', () => {
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type('Scheduled Title');
            cy.get('#desc').type('Test description');
            cy.get('#enableScheduling').check();
            cy.get('#repetitionPeriod').select('3');
            cy.get('#numberOfRepetitions').select('2');
            cy.get('#scheduleEmail').clear();
            cy.get('#scheduleEmail').type('user@example.org');
            cy.get('#request').click();
            cy.wait('@create').then((interception) => {
              expect(interception.request.body).to.have.property(
                'scheduled_repetitions'
              );
              expect(
                interception.request.body.scheduled_repetitions
              ).to.deep.equal({
                repetition_period_in_months: 3,
                number_of_repetitions: 2,
                email: 'user@example.org',
              });
            });
          });

          it('submits without email when email is empty', () => {
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type('Scheduled Title');
            cy.get('#desc').type('Test description');
            cy.get('#enableScheduling').check();
            cy.get('#repetitionPeriod').select('1');
            cy.get('#numberOfRepetitions').select('1');
            cy.get('#scheduleEmail').clear();
            cy.get('#request').click();
            cy.wait('@create').then((interception) => {
              expect(interception.request.body).to.have.property(
                'scheduled_repetitions'
              );
              expect(
                interception.request.body.scheduled_repetitions
              ).to.not.have.property('email');
            });
          });

          it('does not include scheduled_repetitions when scheduling is disabled', () => {
            cy.get('#zimtitle').clear();
            cy.get('#zimtitle').type('No Schedule Title');
            cy.get('#desc').type('Test description');
            cy.get('#request').click();
            cy.wait('@create').then((interception) => {
              expect(interception.request.body).to.not.have.property(
                'scheduled_repetitions'
              );
            });
          });
        });

        describe('when there is an active schedule', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_with_schedule.json',
            }).as('status');
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('displays the active schedule warning', () => {
            cy.contains('Active schedule found').should('be.visible');
          });

          it('shows the correct interval in the warning', () => {
            cy.contains('3 months').should('be.visible');
          });

          it('shows the next generation date', () => {
            cy.contains('2026-06-01').should('be.visible');
          });

          it('shows the Delete schedule button', () => {
            cy.contains('button', 'Delete schedule').should('be.visible');
            cy.contains('button', 'Delete schedule').should(
              'not.have.attr',
              'disabled'
            );
          });

          it('does not show the request form', () => {
            cy.get('#desc').should('not.exist');
            cy.get('#longdesc').should('not.exist');
            cy.get('#request').should('not.exist');
          });

          describe('when the Delete schedule button is clicked', () => {
            beforeEach(() => {
              cy.intercept('DELETE', 'v1/builders/1/schedule', {
                statusCode: 200,
                body: {},
              }).as('deleteSchedule');
              // After deletion, status returns without schedule
              cy.intercept('v1/builders/1/zim/status', {
                fixture: 'zim_status_not_requested.json',
              }).as('statusAfterDelete');
            });

            it('sends the DELETE request', () => {
              cy.contains('button', 'Delete schedule').click();
              cy.wait('@deleteSchedule');
            });

            it('shows the request form after deletion', () => {
              cy.contains('button', 'Delete schedule').click();
              cy.wait('@deleteSchedule');
              cy.wait('@statusAfterDelete');
              cy.get('#desc').should('be.visible');
              cy.get('#longdesc').should('be.visible');
            });
          });
        });

        describe('when there is an active schedule and ZIM is REQUESTED', () => {
          beforeEach(() => {
            cy.intercept('v1/builders/1/zim/status', {
              fixture: 'zim_status_with_schedule_requested.json',
            }).as('status');
            cy.visit('/#/selections/1/zim');
            cy.wait('@identity');
            cy.wait('@builder');
            cy.wait('@status');
          });

          it('does not show the active schedule warning', () => {
            cy.contains('Active schedule found').should('not.exist');
          });

          it('shows the Download ZIM button disabled', () => {
            cy.get('#download').should('be.visible');
            cy.get('#download').should('have.attr', 'disabled');
          });

          it('shows the building indicator', () => {
            cy.contains('Building…').should('be.visible');
          });
        });
      });

      describe('and the selection is over the article limit', () => {
        beforeEach(() => {
          cy.intercept('GET', 'v1/builders/1/selection/latest/article_count', {
            selection: {
              id: '1',
              article_count: 100000,
              max_article_count: 50000,
            },
          }).as('article_count');
          cy.intercept('v1/builders/1/zim/status', {
            fixture: 'zim_status_not_requested.json',
          }).as('status');
        });

        it('displays the article error message and disables the request', () => {
          cy.visit('/#/selections/1/zim');
          cy.wait('@identity');
          cy.wait('@builder');
          cy.wait('@status');
          cy.contains('Too many articles');
          cy.get('#request').should('have.attr', 'disabled');
        });
      });
    });

    describe('and the builder is not found', () => {
      beforeEach(() => {
        cy.intercept('GET', 'v1/builders/1', {
          statusCode: 404,
          body: '404 NOT FOUND',
        });
        cy.visit('/#/selections/1/zim');
      });

      it('displays the 404 text', () => {
        cy.contains('404 Not Found').should('be.visible');
      });
    });
  });

  describe('when the user is not logged in', () => {
    it('shows the signed-out explanation', () => {
      cy.visit('/#/selections/1/zim');
      cy.contains('a', 'Sign in with Wikipedia');
    });
  });
});
