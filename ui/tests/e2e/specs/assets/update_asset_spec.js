describe("Update Asset Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to Assets page", function() {
    cy.visit("/assets");
  });

  it("WHEN: Event planner updates an asset", function() {
    cy.get("[data-cy=edit-asset]")
      .eq(0)
      .click();

    cy.get("[data-cy=description]").type(" V2");

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: Asset description is changed", function() {
    cy.get("tbody").contains(" V2");
  });
});
