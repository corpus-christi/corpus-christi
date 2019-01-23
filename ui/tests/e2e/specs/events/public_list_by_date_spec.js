// NOTE: Needs specific dates to pass tests
describe("Public List by Date Test", function() {
  it("GIVEN: User navigates to events page", function() {
    cy.visit("/public/events");
  });

  it("WHEN: User specifies a specific date range", function() {
    cy.get("[data-cy=end-date-picker]").click();

    cy.get(
      ".v-date-picker-header > :nth-child(1) > .v-btn__content > .v-icon"
    ).click();
    cy.get(":nth-child(4) > :nth-child(7) > .v-btn")
      .eq(1)
      .click();
  });

  it("THEN: Events that only start in the specified date range appear", function() {
    cy.get(".container").should("not.contain", "1/20/2019");

    cy.get(".container").contains("1/18/2019");
    cy.get(".container").contains("1/19/2019");
  });
});
