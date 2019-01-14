describe('Archive Event Test', function() {
  it('GIVEN: Event Planner goes to Event page', function() {
    cy.visit('/login');
    cy.get('[data-cy=username]').type('Cytest');
    cy.get('[data-cy=password]').type('password');
    cy.get('[data-cy=login]').click();
    cy.url().should('include', '/admin');
    cy.visit('/events/all');
  });

  it('WHEN: Event Planner wants to deactivate an event', function() {
    cy.get('[data-cy=archive').click();
    cy.get('[data-cy=confirm-archive').click();
  });

  it('THEN: ', function() {

  });
});
