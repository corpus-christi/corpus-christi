describe("Update Team Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to teams page", function() {
    cy.visit("/teams/all");
  });

  it("WHEN: Event planner updates a team name", function() {
    cy.get("[data-cy=edit-team]")
      .eq(0)
      .click();

    cy.get("[data-cy=description]").type(" V2");

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: Updated team appears in table", function() {
    cy.get("tbody").contains(" V2");
  });
});
