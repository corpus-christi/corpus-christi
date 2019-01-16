describe("Archive Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event Planner goes to Event page", function() {
    cy.visit("/events/all");
  });

  it("WHEN: Event Planner wants to deactivate an event", function() {
    // Change the view to see both active and archived events
    cy.get(".md3 > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-select__selections").click();
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile > .v-list__tile__content > .v-list__tile__title").click();

    // Also view past events
    cy.get("[data-cy=view-past-switch]").eq(0).click();

    cy.get("[data-cy=archive]")
      .eq(0)
      .click();
    cy.get("[data-cy=confirm-archive]").click();
  });

  it("THEN: Event is listed as archived", function() {
    cy.get("[data-cy=unarchive]").eq(0).should("exist");
  });

  it("AND: Event can be unarchived", function() {
    cy.get("[data-cy=unarchive]")
      .eq(0)
      .click();
    cy.get(":nth-child(1) > :nth-child(4)")
      .get("[data-cy=archive]").eq(0)
      .should("exist");
  });
});
