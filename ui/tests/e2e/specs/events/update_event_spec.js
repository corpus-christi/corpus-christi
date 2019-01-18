describe("Update Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event Planner goes to Event page", function() {
    cy.visit("/events/all");
  });

  it("WHEN: Event Planner wants to update an event", function() {
    // Put a new title on the event
    cy.get("[data-cy=edit]")
      .eq(0)
      .click();
    cy.get("[data-cy=title]").type(" V2");

    // Rewrite a new description of the event
    cy.get("[data-cy=description]").clear();
    cy.get("[data-cy=description]").type("A whole new description.");

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: Event title should be updated", function() {
    // Switch to see all events on one page
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot"
    ).click();
    cy.contains("Todos").click();

    // Check for new title in table
    cy.get(":nth-child(1) > :nth-child(1)").contains(" V2");
  });

  it("AND: The event description should be updated", function() {
    cy.get("[data-cy=edit]")
      .eq(0)
      .click();

    cy.get("[data-cy=description]").should(
      "have.value",
      "A whole new description."
    );
  });
});
