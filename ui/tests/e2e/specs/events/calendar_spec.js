// NOTE: Requires selection of an event through the style tag
describe("Calendar Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to the calendar", function() {
    cy.visit("/events/all");
    cy.get("[data-cy=calendar]").click();
  });

  it("WHEN: Event planner clicks on a specific event", function() {
    // TODO: Investigate routing issues
    // Get style tag of an event
    cy.get("[style='top: 626px;'] > .vuecal__event-content > a").click();
  });

  it("THEN: Event planner taken to event details page", function() {
    cy.url().should("include", "/details");
  });
});
