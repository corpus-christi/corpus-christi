describe('Create Event Test', function() {
  it('GIVEN: Event Planner goes to Event page', function() {
    cy.visit('/login');
    cy.get('[data-cy=username]').type('Cytest');
    cy.get('[data-cy=password]').type('password');
    cy.get('[data-cy=login]').click();
    cy.visit('/events/all');
  });

  it('WHEN: Event Planner adds a new event and fills out details', function() {
    cy.get('[data-cy=add-event').click();
    cy.get('[data-cy=title]').type('New Event');

    cy.get('[data-cy=description]').type('A neat description of something.');

    cy.get('[data-cy=start-date-menu]').click();
    // Get cypress to click on a certain position on the calendar
    cy.get('tbody > :nth-child(3) > :nth-child(1) > .v-btn > .v-btn__content').click();

    cy.get('[data-cy=start-time-dialog]').click();
    // Cypress clicks a style position for hour
    cy.get('[style="left: 76.8468%; top: 34.5%;"]').click();
    // Click randomly for minute
    cy.get('.v-time-picker-clock__inner').eq(1).click();
   
    cy.get('[data-cy=start-time-ok]').click();
    cy.get('[data-cy=end-date-menu]').click();
    // Get cypress to click on a certain position on the calendar
    cy.get('[data-cy=end-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-table > table > tbody > :nth-child(3) > :nth-child(1) > .v-btn > .v-btn__content')
      .click();

    cy.get('[data-cy=end-time-dialog]').click();
    // Cypress clicks a style position for hour
    cy.get('[style="left: 76.8468%; top: 65.5%;"]').click();
    // Click randomly for minute
    cy.get('.v-time-picker-clock__inner').eq(1).click();

    cy.get('[data-cy=end-time-ok]').click();
    cy.get('[data-cy=form-save]').click();
  });

  it('THEN: A new event is listed in the table', function() {
    cy.get('tbody').contains('New Event');
  });
});
