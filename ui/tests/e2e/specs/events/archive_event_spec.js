describe("Archive Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event Planner goes to Event page", function() {
    cy.visit("/events/all");
  });

  it("WHEN: Event Planner wants to deactivate an event", function() {
    // See all archived, active, and past events
    cy.get(
      ".layout > :nth-child(1) > .v-input > .v-input__control > .v-input__slot"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile > .v-list__tile__content"
    ).click();
    cy.get("[data-cy=view-past-switch]")
      .eq(0)
      .click();

    cy.get("[data-cy=archive]")
      .eq(0)
      .click();
    cy.get("[data-cy=confirm-archive]").click();
  });

  it("THEN: Event is listed as archived", function() {
    cy.get("[data-cy=unarchive]")
      .eq(0)
      .should("exist");
  });

  it("AND: Event can be unarchived", function() {
    cy.get("[data-cy=unarchive]")
      .eq(0)
      .click();
    cy.get(":nth-child(1) > :nth-child(4)")
      .get("[data-cy=archive]")
      .eq(0)
      .should("exist");
  });
});
