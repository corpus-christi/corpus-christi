// NOTE: Requires specific data
describe("Calendar Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to the calendar", function() {
    cy.visit("/events/calendar");
  });

  it("WHEN: Event planner clicks on a specific event", function() {
    // Grab by span instead of link
    cy.get(
      ":nth-child(2) > .vuecal__cell-content > .vuecal__cell-events > .vuecal__event--overlapped.vuecal__event--split2 > .vuecal__event-time"
    ).click();
  });

  it("THEN: Event planner taken to event details page", function() {
    cy.url().should("include", "/details");
  });
});
