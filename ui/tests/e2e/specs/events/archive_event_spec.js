// TODO: Skeleton done, needs more extensive testing
describe("Archive Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event Planner goes to Event page", function() {
    cy.visit("/events/all");
  });

  // TODO: Eventually get by ID
  it("WHEN: Event Planner wants to deactivate an event", function() {
    cy.get("[data-cy=archive]")
      .eq(0)
      .click();
    cy.get("[data-cy=confirm-archive]").click();
  });

  it("THEN: Event is listed as archived", function() {
    cy.get("[data-cy=unarchive]").should("exist");
  });

  // TODO: Also test for unarchiving events, bad test data
  it("AND: Event can be unarchived", function() {
    cy.get("[data-cy=unarchive]")
      .eq(0)
      .click();
    cy.get(":nth-child(1) > :nth-child(4)")
      .find("[data-cy=archive]")
      .should("exist");
  });
});
