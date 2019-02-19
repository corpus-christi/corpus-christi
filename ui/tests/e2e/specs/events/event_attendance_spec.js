describe("Attendance Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to a specific event", function() {
    cy.visit("/event/1/details");
  });

  it("WHEN: Event planner adds an attendance number", function() {
    cy.get("[data-cy=edit-attendance]").click();

    cy.get("[data-cy=attendance-input]").clear();
    cy.get("[data-cy=attendance-input]").type("1234");

    cy.get("[data-cy=attendance-save]").click();
  });

  it("THEN: Attendance number is updated", function() {
    cy.get(".layout > :nth-child(1) > :nth-child(1) > span").contains("1234");
  });
});
