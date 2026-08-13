/// <reference types="Cypress" />

describe('the selection detail editor', () => {
  const visitEditor = (builderFixture) => {
    cy.intercept('v1/selection/lists', {
      fixture: 'list_data.json',
    }).as('list');
    cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as('login');
    cy.intercept('GET', 'v1/builders/1', { fixture: builderFixture }).as(
      'builder'
    );
    cy.visit('/#/selections/user/1/edit');
    cy.wait('@login');
    cy.wait('@list');
    cy.wait('@builder');
  };

  describe('for a simple selection', () => {
    beforeEach(() => {
      visitEditor('simple_builder.json');
    });

    it('shows the collapsed rail and the field rows', () => {
      cy.get('#row-name').contains('Builder 1');
      cy.get('#row-list').contains('2 titles');
      cy.get('#row-project').contains('en.wiktionary.org');
      cy.get('#row-schedule').contains('None — set one up when creating a ZIM');
      // No save has happened yet, so no save state is claimed.
      cy.get('#save-indicator').should('not.exist');
    });

    it('opens a field for editing on click and cancels with Escape', () => {
      cy.get('#row-name').click();
      cy.get('#edit-name').should('have.value', 'Builder 1');
      cy.get('#edit-name').type('{esc}');
      cy.get('#edit-name').should('not.exist');
      cy.get('#row-name').should('be.visible');
    });

    it('saves an edited name', () => {
      cy.intercept('POST', 'v1/builders/1', (req) => {
        expect(req.body.name).to.equal('Renamed Builder');
        expect(req.body.model).to.equal('wp1.selection.models.simple');
        expect(req.body.params.list).to.deep.equal([
          'Eiffel_Tower',
          'Statue_of_Liberty',
        ]);
        req.reply({
          statusCode: 200,
          body: { success: true, id: '1', items: {} },
        });
      }).as('save');
      cy.get('#row-name').click();
      cy.get('#edit-name').clear();
      cy.get('#edit-name').type('Renamed Builder');
      cy.get('#save-name').click();
      cy.wait('@save');
      cy.get('#save-indicator').contains('All changes saved');
      cy.get('#edit-name').should('not.exist');
    });

    it('edits the article list in a mono textarea', () => {
      cy.intercept('POST', 'v1/builders/1', (req) => {
        expect(req.body.params.list).to.deep.equal([
          'Eiffel_Tower',
          'Statue_of_Liberty',
          'Freedom_Monument_(Baghdad)',
        ]);
        req.reply({
          statusCode: 200,
          body: { success: true, id: '1', items: {} },
        });
      }).as('save');
      cy.get('#row-list').click();
      cy.get('#edit-list').should(
        'have.value',
        'Eiffel_Tower\nStatue_of_Liberty'
      );
      cy.get('#edit-list').type('\nFreedom_Monument_(Baghdad)');
      cy.get('#save-list').click();
      cy.wait('@save');
    });

    it('rejects an empty article list client-side', () => {
      cy.get('#row-list').click();
      cy.get('#edit-list').clear();
      cy.get('#save-list').click();
      cy.contains('Please provide at least one article title.');
      cy.get('#edit-list').should('be.visible');
    });

    it('shows validation errors and keeps the field open', () => {
      cy.intercept('POST', 'v1/builders/1', {
        fixture: 'save_list_failure.json',
      }).as('save');
      cy.get('#row-list').click();
      cy.get('#edit-list').type('\nStatue of#Liberty');
      cy.get('#save-list').click();
      cy.wait('@save');
      cy.get('#save-indicator').contains("Couldn't save");
      cy.contains('The list contained the following invalid characters: #');
      cy.get('#edit-list').should('be.visible');
    });

    it('shows the Remove action and deletes an active schedule', () => {
      cy.intercept('v1/builders/1/zim/status', {
        fixture: 'zim_status_with_schedule.json',
      });
      cy.intercept('DELETE', 'v1/builders/1/schedule', {
        statusCode: 204,
        body: '',
      }).as('deleteSchedule');
      // Reload so the schedule status is picked up. (cy.visit with the same
      // URL is a hash-only navigation and would not refetch.)
      cy.reload();
      cy.get('#row-schedule').contains('Every 3 months');
      cy.get('#remove-schedule').click();
      // Clicking elsewhere on the row must not remove the schedule; an
      // inline confirm strip appears instead of a native dialog.
      cy.get('#confirm-remove-schedule').click();
      cy.wait('@deleteSchedule');
    });

    it('cancels schedule removal from the confirm strip', () => {
      cy.intercept('v1/builders/1/zim/status', {
        fixture: 'zim_status_with_schedule.json',
      });
      cy.reload();
      cy.get('#remove-schedule').click();
      cy.get('#cancel-remove-schedule').click();
      cy.get('#confirm-remove-schedule').should('not.exist');
      cy.get('#row-schedule').contains('Every 3 months');
    });

    it('deletes the selection from the footer', () => {
      cy.intercept('v1/builders/1/delete-impact', {
        fixture: 'delete_impact_none.json',
      });
      cy.intercept('POST', 'v1/builders/1/delete', {
        statusCode: 200,
        body: { status: '204' },
      }).as('delete');
      cy.get('#delete-button').click();
      cy.get('#delete-impact-dialog').should('be.visible');
      cy.get('#confirmDeleteButton').click();
      cy.wait('@delete');
      cy.get('#delete-impact-dialog').should('not.exist');
      cy.url().should('include', '/selections/user');
    });

    describe('when combinators depend on this selection', () => {
      beforeEach(() => {
        cy.intercept('v1/builders/1/delete-impact', {
          fixture: 'delete_impact_combinators.json',
        });
        cy.intercept('POST', 'v1/builders/1/delete', {
          statusCode: 200,
          body: { status: '204' },
        }).as('delete');
        cy.get('#delete-button').click();
      });

      it('requires a decision and a typed confirmation', () => {
        cy.get('#delete-impact-dialog').contains('Keepable Combo');
        cy.get('#delete-impact-dialog').contains('Empty Combo');
        // Auto-deleted combinators are pre-decided and disabled.
        cy.get('#remove-builder-combo-empty').should('be.disabled');
        cy.get('#delete-combinator-combo-empty').should('be.checked');
        // Confirm stays disabled until a decision is made and the name typed.
        cy.get('#confirmDeleteButton').should('have.attr', 'disabled');
        cy.get('#remove-builder-combo-keep').check();
        cy.get('#confirmDeleteButton').should('have.attr', 'disabled');
        cy.get('#delete-confirm-name').type('Builder 1');
        cy.get('#confirmDeleteButton').should('not.have.attr', 'disabled');
      });

      it('sends the chosen combinator deletions', () => {
        cy.get('#delete-combinator-combo-keep').check();
        cy.get('#delete-confirm-name').type('Builder 1');
        cy.get('#confirmDeleteButton').click();
        cy.wait('@delete').then((interception) => {
          expect(interception.request.body.delete_combinator_ids).to.deep.equal(
            ['combo-keep']
          );
          expect(interception.request.body.confirm_builder_name).to.equal(
            'Builder 1'
          );
        });
      });
    });
  });

  describe('for a SPARQL selection', () => {
    beforeEach(() => {
      visitEditor('sparql_builder.json');
    });

    it('shows the query field row', () => {
      cy.get('#row-query').contains('SELECT ?foo WHERE {}');
    });

    it('edits the query', () => {
      cy.intercept('POST', 'v1/builders/1', (req) => {
        expect(req.body.params.query).to.contain('SELECT');
        req.reply({
          statusCode: 200,
          body: { success: true, id: '1', items: {} },
        });
      }).as('save');
      cy.get('#row-query').click();
      cy.get('#edit-query').should('contain.value', 'SELECT ?foo');
      cy.get('#save-query').click();
      cy.wait('@save');
    });
  });

  describe('for a WikiProject selection', () => {
    beforeEach(() => {
      visitEditor('wikiproject_builder.json');
    });

    it('shows include and exclude rows', () => {
      cy.get('#row-wp_include').contains('British Columbia road transport');
      cy.get('#row-wp_exclude').contains('Countries');
    });

    it('edits the include list with the autocomplete', () => {
      cy.intercept('POST', 'v1/builders/1', (req) => {
        expect(req.body.params.include).to.include('Water');
        expect(req.body.params.include).to.include(
          'British Columbia road transport'
        );
        req.reply({
          statusCode: 200,
          body: { success: true, id: '1', items: {} },
        });
      }).as('save');
      cy.get('#row-wp_include').click();
      cy.get('input[placeholder="WikiProject name"]').type('Water');
      cy.contains('li', /^\s*Water\s*$/).click();
      cy.get('#save-wp_include').click();
      cy.wait('@save');
    });

    it('requires at least one included WikiProject', () => {
      cy.get('#row-wp_include').click();
      // Remove both chips.
      cy.get('button[aria-label^="Remove"]').first().click();
      cy.get('button[aria-label^="Remove"]').first().click();
      cy.get('#save-wp_include').click();
      cy.contains('Please provide at least one WikiProject.');
    });
  });

  describe('selection errors', () => {
    it('shows a retryable error with a Retry button that re-saves', () => {
      visitEditor('simple_builder_retryable_error.json');
      cy.get('#selection-errors').contains('There was a timeout.');
      cy.intercept('POST', 'v1/builders/1', {
        statusCode: 200,
        body: { success: true, id: '1', items: {} },
      }).as('retry');
      cy.get('#retry-button').click();
      cy.wait('@retry');
    });

    it('shows a fatal error without a Retry button', () => {
      visitEditor('simple_builder_fatal_error.json');
      cy.get('#selection-errors').should('be.visible');
      cy.get('#retry-button').should('not.exist');
      cy.contains("This error can't be retried");
    });
  });

  describe('old edit URLs', () => {
    beforeEach(() => {
      cy.intercept('v1/selection/lists', { fixture: 'list_data.json' });
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
      cy.intercept('GET', 'v1/builders/1', { fixture: 'simple_builder.json' });
    });

    it('redirects /selections/simple/1 to the detail editor', () => {
      cy.visit('/#/selections/simple/1');
      cy.url().should('include', '/selections/user/1/edit');
      cy.get('#row-name').contains('Builder 1');
    });

    it('redirects /selections/sparql/1 to the detail editor', () => {
      cy.visit('/#/selections/sparql/1');
      cy.url().should('include', '/selections/user/1/edit');
    });
  });
});
