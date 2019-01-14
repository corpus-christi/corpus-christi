// TODO: Skeleton done, needs more extensive testing
describe('Archive Event Test', function() {
  it('GIVEN: Event Planner goes to Event page', function() {
    cy.visit('/login');
    cy.get('[data-cy=username]').type('Cytest');
    cy.get('[data-cy=password]').type('password');
    cy.get('[data-cy=login]').click();
    cy.url().should('include', '/admin');
    cy.visit('/events/all');
  });

  // TODO: Eventually get by ID
  it('WHEN: Event Planner wants to deactivate an event', function() {
    cy.get('[data-cy=archive').eq(0).click();
    cy.get('[data-cy=confirm-archive').click();
  });

  it('THEN: ', function() {
    cy.get('[data-cy=unarchive').should('exist');
  });

  // TODO: Also test for unarchiving events
});
