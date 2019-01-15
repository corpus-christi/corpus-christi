// TODO: Finish writing full test
describe("Read Event Test", function() {
  before(() => {
    cy.login();
  })

  it("GIVEN: Event Planner goes to a specific event", function() {
    cy.visit("/events/2/details");
  });

  it("WHEN: Event planner wants to see the details of an event", function() {
    // TODO: Read event details
    // TODO: Read event participants
    // TODO: Read event teams
    // TODO: Read event assets
  });
});
