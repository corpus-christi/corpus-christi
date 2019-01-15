// TODO: Skeleton done for now, should do more extensive testing later
describe("Update Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event Planner goes to Event page", function() {
    cy.visit("/events/all");
  });

  it("WHEN: Event Planner wants to update an event", function() {
    cy.get("[data-cy=edit]")
      .eq(0)
      .click();
    cy.get("[data-cy=title]").type(" V2");

    // Rewrite a new description of the event
    // TODO: Check for updated description
    cy.get("[data-cy=description]").clear();
    cy.get("[data-cy=description]").type("Join us for a whole day of prayer.");

    cy.get("[data-cy=form-save]").click();
  });

  // TODO: Search table by ID
  it("THEN: Event details should be updated", function() {
    // Check for new title in table
    cy.get("tbody").contains(" V2");
  });
});
