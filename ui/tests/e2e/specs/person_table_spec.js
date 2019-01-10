describe('PersonTable Test', function() {
  it('GIVEN: Admin loads PersonTable', function() {
    cy.visit('/login');
    cy.get('[data-cy=username]').type('Cytest');
    cy.get('[data-cy=password]').type('password');
    cy.get('[data-cy=login]').click();
    cy.visit('/people');
  });

  it('WHEN: Admin changes table view', function() {
    cy.get('[data-cy=person-table]').find('.v-input__control').click();
    // TODO: Ugly way to change the number of rows, alternative???
    cy.contains('10').click();
  });

  it('THEN: Table shows more rows', function() {
    cy.get('tbody').find('tr').should('have.length', 10);
  });

  // TODO: Test switching through pages of the table
  // it('AND: Table shows next page', function() {
  //   cy.get('[data-cy=person-table]').find('.v-icon material-icons theme--light').click();
  // });
});