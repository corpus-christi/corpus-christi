// TODO: Skeleton done, needs more extensive tests
describe('Duplicate Event Test', function() {
  it('GIVEN: Event Planner goes to Event page', function() {
    cy.visit('/login');
    cy.get('[data-cy=username]').type('Cytest');
    cy.get('[data-cy=password]').type('password');
    cy.get('[data-cy=login]').click();
    cy.url().should('include', '/admin');
    cy.visit('/events/all');
  });

  it('WHEN: Event planner duplicates an event', function() {
    cy.get('[data-cy=duplicate]').click();

    cy.get('[data-cy=start-date-menu').click();
    cy.get(':nth-child(5) > :nth-child(2) > .v-btn > .v-btn__content').click();

    cy.get('[data-cy=end-date-menu').click();
    cy.get('[data-cy=end-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-table > table > tbody > :nth-child(5) > :nth-child(2)')
      .click();

    cy.get('[data-cy=form-save]').click();
  });

  it('THEN: A new event is created with a different time', function() {
    cy.get('tbody').contains('28/1/2019 14:45');
  });
});
