// TODO: Wait for UI to finish with updating events
describe('Create Event Test', function() {
  it('GIVEN: Event Planner goes to Event page', function() {
    cy.visit('/login');
    cy.get('[data-cy=username]').type('Cytest');
    cy.get('[data-cy=password]').type('password');
    cy.get('[data-cy=login]').click();
    cy.url().should('include', '/admin');
    cy.visit('/events/all');
  });

  it('WHEN: Event Planner wants to update an event', function() {
    cy.get('[data-cy=edit]').eq(0).click();
    cy.get('[data-cy=title]').type(' V2');
    
    cy.get('[data-cy=description]').clear();
    cy.get('[data-cy=description]').type('Join us for a whole day of prayer.');
  });

  it('THEN: Event details should be updated', function() {
  });
});
