/// <reference types="Cypress" />

describe('the selections page', () => {
  const stubDetailFor = (id, builderFixture) => {
    cy.intercept('GET', `v1/builders/${id}`, {
      fixture: builderFixture,
    }).as('builder');
    cy.intercept(`v1/builders/${id}/zim/status`, {
      fixture: 'zim_status_not_requested.json',
    }).as('zimStatus');
    cy.intercept(`v1/builders/${id}/selection/latest/article_count`, {
      body: {
        selection: { id: 'abcd', article_count: 34, max_article_count: 50000 },
      },
    }).as('articleCount');
    cy.intercept(`v1/builders/${id}/delete-impact`, {
      fixture: 'delete_impact_none.json',
    }).as('deleteImpact');
  };

  describe('when the user is logged in', () => {
    beforeEach(() => {
      cy.intercept('v1/selection/lists', {
        fixture: 'list_data.json',
      }).as('list');
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'login'
      );
      stubDetailFor(1, 'simple_builder.json');
      cy.visit('/#/selections/user');
      cy.wait('@login');
      cy.wait('@list');
    });

    it('successfully loads', () => {});

    it('displays the selection rail with all rows', () => {
      cy.contains('.wp1r-railrow', 'simple list');
      cy.contains('.wp1r-railrow', 'sparql list');
      cy.contains('.wp1r-railrow', 'combinator list');
    });

    it('derives the status vocabulary for each row', () => {
      cy.contains('.wp1r-railrow', 'zim ready').contains('Up to date');
      cy.contains('.wp1r-railrow', 'outdated zim').contains('Stale');
      cy.contains('.wp1r-railrow', 'deleted zim').contains('Expired');
      cy.contains('.wp1r-railrow', 'zim requested').contains('Building');
      cy.contains('.wp1r-railrow', 'updated list').contains('Processing');
      cy.contains('.wp1r-railrow', 'permanent error').contains('Failed');
      cy.contains('.wp1r-railrow', 'zim failed').contains('Failed');
      cy.contains('.wp1r-railrow', 'combinator broken reference').contains(
        'Failed'
      );
      cy.contains('.wp1r-railrow', 'selection ready, no zim').contains(
        'No ZIM'
      );
      cy.contains('.wp1r-railrow', 'simple list').contains('No ZIM');
    });

    it('shows the count chips', () => {
      cy.contains('button', 'All 15');
      cy.contains('button', 'Needs attention 7');
      cy.contains('button', 'Up to date 1');
      cy.contains('button', 'No ZIM 10');
      cy.contains('button', 'Scheduled 1');
    });

    it('auto-selects the first selection on desktop', () => {
      cy.url().should('include', '/selections/user/1');
      cy.get('#detail-title').should('contain.text', 'simple list');
    });

    it('shows the detail pane for the selected row', () => {
      cy.wait('@builder');
      cy.wait('@articleCount');
      cy.contains('34 articles');
      cy.get('#definition').should('contain.text', 'Eiffel_Tower');
      cy.contains('a', 'Article list (TSV)').should(
        'have.attr',
        'href',
        'https://www.example.fake/abcd-efgh'
      );
      cy.contains('No ZIM file yet');
    });

    it('hides the stale article count while the selection is re-processing', () => {
      stubDetailFor(
        'aafcc4a2-cd5c-4236-85ca-3a10d16f13aa',
        'simple_builder.json'
      );
      cy.contains('.wp1r-railrow', 'updated list').click();
      cy.wait('@articleCount');
      cy.get('#detail-title').should('contain.text', 'updated list');
      cy.contains('34 articles').should('not.exist');
    });

    it('disables Create ZIM when the selection failed to materialize', () => {
      stubDetailFor(
        '7368f534-27f5-4350-bfe3-23b90363df7b',
        'simple_builder_fatal_error.json'
      );
      cy.contains('.wp1r-railrow', 'permanent error').click();
      cy.get('#create-zim-button')
        .should('match', 'button')
        .and('have.attr', 'disabled');
      // A cleanly materialized selection keeps the real link.
      cy.contains('.wp1r-railrow', 'simple list').click();
      cy.get('#create-zim-button')
        .should('match', 'a')
        .and('have.attr', 'href', '#/selections/1/zim');
    });

    it('shows an error with retry when the builder fetch fails', () => {
      cy.intercept('GET', 'v1/builders/1', { statusCode: 500, body: {} }).as(
        'builderFail'
      );
      cy.reload();
      cy.wait('@builderFail');
      // Scope to the desktop pane: the hidden mobile detail instance
      // renders its own copy of the error element.
      cy.get('.md\\:grid')
        .find('#builder-load-error')
        .contains("Couldn't load this selection.");
      cy.intercept('GET', 'v1/builders/1', {
        fixture: 'simple_builder.json',
      }).as('builderRetry');
      cy.get('.md\\:grid').find('#retry-load-builder').click();
      cy.wait('@builderRetry');
      cy.get('#definition').should('contain.text', 'Eiffel_Tower');
      cy.get('.md\\:grid').find('#builder-load-error').should('not.exist');
    });

    it('shows the stat strip with selection and ZIM statuses', () => {
      cy.contains('.wp1r-stat', 'Selection').contains('Ready');
      cy.contains('.wp1r-stat', 'ZIM').contains('No ZIM');
      cy.contains('.wp1r-stat', 'Schedule').contains('None');
    });

    it('hides the TSV link while the selection is processing', () => {
      cy.contains('.wp1r-railrow', 'updated list').click();
      cy.contains('.wp1r-stat', 'Selection').contains('Processing…');
      cy.contains('Article list not ready yet');
      cy.contains('a', 'Article list (TSV)').should('not.exist');
    });

    it('links Create ZIM to the ZIM page', () => {
      cy.get('#create-zim-button').should(
        'have.attr',
        'href',
        '#/selections/1/zim'
      );
    });

    it('links Edit to the detail editor', () => {
      cy.get('#edit-button').should(
        'have.attr',
        'href',
        '#/selections/user/1/edit'
      );
    });

    it('filters rows by name', () => {
      cy.get('input[placeholder="Filter…"]').first().type('combinator');
      cy.contains('.wp1r-railrow', 'combinator list');
      cy.contains('.wp1r-railrow', 'simple list').should('not.exist');
    });

    it('filters rows by type', () => {
      cy.get('input[placeholder="Filter…"]').first().type('sparql');
      cy.contains('.wp1r-railrow', 'permanent error');
      cy.contains('.wp1r-railrow', 'simple list').should('not.exist');
    });

    it('shows an empty state when no rows match the filter', () => {
      cy.get('input[placeholder="Filter…"]').first().type('zzzzz');
      cy.contains('No selections match.');
      cy.contains('button', 'Clear filters').click();
      cy.contains('.wp1r-railrow', 'simple list');
    });

    it('filters by status when a chip is clicked', () => {
      cy.contains('button', 'Needs attention 7').click();
      cy.contains('.wp1r-railrow', 'permanent error');
      cy.contains('.wp1r-railrow', 'simple list').should('not.exist');
      // Clicking again clears the filter.
      cy.contains('button', 'Needs attention 7').click();
      cy.contains('.wp1r-railrow', 'simple list');
    });

    it('focuses the filter input when / is pressed', () => {
      cy.get('body').type('/');
      cy.get('input[placeholder="Filter…"]').first().should('have.focus');
    });

    it('navigates to another selection when its row is clicked', () => {
      stubDetailFor('sched-builder-001', 'simple_builder.json');
      cy.contains('.wp1r-railrow', 'scheduled zim').click();
      cy.url().should('include', '/selections/user/sched-builder-001');
    });

    it('shows the schedule in the stat strip for a scheduled selection', () => {
      cy.intercept('GET', 'v1/builders/sched-builder-001', {
        fixture: 'simple_builder.json',
      });
      cy.intercept('v1/builders/sched-builder-001/zim/status', {
        fixture: 'zim_status_with_schedule.json',
      });
      cy.contains('.wp1r-railrow', 'scheduled zim').click();
      cy.contains('Every 3 months');
    });

    it('shows the stale banner for an outdated zim', () => {
      stubDetailFor(
        'dcea7035-cc69-471e-b0e6-08dfbafd5e7c',
        'simple_builder.json'
      );
      cy.contains('.wp1r-railrow', 'outdated zim').click();
      cy.get('#stale-banner').should('be.visible');
      cy.contains('Rebuild ZIM');
    });

    it('shows the selection error banner with retry for retryable errors', () => {
      cy.intercept('GET', 'v1/builders/7368f534-27f5-4350-bfe3-23b90363df7b', {
        fixture: 'sparql_builder_retryable_error.json',
      });
      cy.contains('.wp1r-railrow', 'permanent error').click();
      cy.get('#selection-errors').should('be.visible');
      cy.get('#retry-button').should('be.visible');
    });

    it('opens the delete dialog from the overflow menu', () => {
      cy.wait('@builder');
      cy.get('#overflow-button').click();
      cy.get('#delete-menuitem').click();
      cy.get('#delete-impact-dialog').should('be.visible');
      cy.contains('Deleting');
      cy.get('#confirmDeleteButton').should('not.have.attr', 'disabled');
      cy.get('#cancelDeleteButton').click();
      cy.get('#delete-impact-dialog').should('not.exist');
    });

    it('deletes the selection and returns to the list', () => {
      cy.intercept('POST', 'v1/builders/1/delete', {
        statusCode: 200,
        body: { status: '204' },
      }).as('delete');
      cy.wait('@builder');
      cy.get('#overflow-button').click();
      cy.get('#delete-menuitem').click();
      cy.get('#confirmDeleteButton').click();
      cy.wait('@delete');
      cy.get('#delete-impact-dialog').should('not.exist');
      cy.url().should('include', '/selections/user');
    });

    it('shows a not-found pane for an unknown id', () => {
      cy.visit('/#/selections/user/does-not-exist');
      cy.contains('Not found');
    });
  });

  describe('when the list is empty', () => {
    beforeEach(() => {
      cy.intercept('v1/selection/lists', { body: { builders: [] } }).as('list');
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'login'
      );
      cy.visit('/#/selections/user');
      cy.wait('@login');
      cy.wait('@list');
    });

    it('shows the empty state with a New selection button', () => {
      cy.contains("You haven't created a selection yet");
      cy.contains('What you can build');
      cy.contains('a', 'New selection').should(
        'have.attr',
        'href',
        '#/selections/new'
      );
    });
  });

  describe('on mobile', () => {
    beforeEach(() => {
      cy.viewport(390, 844);
      cy.intercept('v1/selection/lists', {
        fixture: 'list_data.json',
      }).as('list');
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' }).as(
        'login'
      );
      cy.visit('/#/selections/user');
      cy.wait('@login');
      cy.wait('@list');
    });

    it('shows the card list without auto-selecting', () => {
      cy.url().should('eq', 'http://localhost:5173/#/selections/user');
      cy.contains('simple list');
      cy.contains('a', 'Build ZIM')
        .first()
        .should('have.attr', 'href', '#/selections/1/zim');
    });

    it('shows the status filter pills', () => {
      cy.contains('button', 'Needs attention');
      cy.contains('button', 'Up to date');
    });

    it('opens the detail view when a card is tapped', () => {
      stubDetailFor(1, 'simple_builder.json');
      cy.get('.md\\:hidden').contains('button', 'simple list').click();
      cy.url().should('include', '/selections/user/1');
      cy.contains('a', '← Selections');
      cy.get('#detail-title').should('contain.text', 'simple list');
    });
  });

  describe('when the list fetch fails', () => {
    it('shows an error with retry instead of the empty state', () => {
      cy.intercept('v1/oauth/identify', { fixture: 'identity.json' });
      cy.intercept('v1/selection/lists', { statusCode: 500, body: {} }).as(
        'listFail'
      );
      cy.visit('/#/selections/user');
      cy.wait('@listFail');
      cy.get('#list-load-error').contains("Couldn't load your selections.");
      // The onboarding empty state must not appear on a server error.
      cy.contains('What you can build').should('not.exist');
      cy.intercept('v1/selection/lists', { fixture: 'list_data.json' }).as(
        'listRetry'
      );
      cy.get('#retry-load-lists').click();
      cy.wait('@listRetry');
      cy.contains('.wp1r-railrow', 'simple list');
    });
  });

  describe('when the user is not logged in', () => {
    it('shows the signed-out explanation with sign in', () => {
      cy.visit('/#/selections/user');
      cy.contains('Selections are lists of Wikipedia articles');
      cy.contains('What you can build');
      cy.contains('a', 'Sign in with Wikipedia');
    });
  });
});
