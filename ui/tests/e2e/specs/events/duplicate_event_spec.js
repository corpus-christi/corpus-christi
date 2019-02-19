describe("Duplicate Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event Planner goes to Event page", function() {
    cy.visit("/events/all");
  });

  it("WHEN: Event planner duplicates an event", function() {
    cy.get("[data-cy=duplicate]")
      .eq(0)
      .click();

    cy.wait(250);

    // Pick a new start and end date
    cy.get("[data-cy=start-date-menu").click();
    cy.get(":nth-child(5) > :nth-child(2) > .v-btn > .v-btn__content").click();

    // TODO: Glitch when picking and end date
    // cy.get("[data-cy=end-date-menu").click();
    // cy.get(
    //   "[data-cy=end-date-picker] > .v-picker__body > :nth-child(1) > .v-date-picker-table > table > tbody > :nth-child(5) > :nth-child(2)"
    // ).click();

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: A new event is created with a different date", function() {
    // Switch to see all events on one page
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot"
    ).click();
    cy.contains("Todos").click();

    cy.get("tbody")
      .eq(1)
      .contains("28/1/2019");
  });
});
