describe("Event Participants Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to an events participants", function() {
    cy.visit("/event/1/participants");
  });

  it("WHEN: Event planner adds a new participant", function() {
    cy.get("[data-cy=add-participant]").click();

    // Wait for the form to fully load
    cy.wait(250);

    // Pick the first person in the list
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();

    cy.get("[data-cy=confirm-participant]").click();
  });

  it("THEN: A new participant is listed", function() {
    cy.get("tbody > :nth-child(1)").should("exist");
  });

  it("AND: Event planner adds another participant", function() {
    cy.get("[data-cy=add-participant]").click();

    // Wait for the form to fully load
    cy.wait(250);

    // Pick the second person in the list
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();

    cy.get("[data-cy=confirm-participant]").click();
  });

  it("THEN: The event has multiple participants", function() {
    cy.get("tbody > :nth-child(2)").should("exist");
  });

  it("AND: Event planner removes a participant", function() {
    cy.get("[data-cy=archive]")
      .eq(0)
      .click();
    cy.get("[data-cy=confirm-delete]")
      .eq(1)
      .click();
  });
});
