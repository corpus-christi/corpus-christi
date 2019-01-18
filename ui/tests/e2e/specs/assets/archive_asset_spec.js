describe("Archive Asset Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to Assets page", function() {
    cy.visit("/assets");
  });

  it("WHEN: Event planner archives an asset", function() {
    cy.get("[data-cy=archive]")
      .eq(0)
      .click();

    cy.get("[data-cy=confirm-archive]").click();

    cy.wait(250);
  });

  it("THEN: Asset is archived", function() {
    cy.get("[data-cy=unarchive]")
      .eq(0)
      .should("exist");
  });

  it("AND: Asset can be unarchived", function() {
    cy.get("[data-cy=unarchive]")
      .eq(0)
      .click();
    cy.get(":nth-child(1) > :nth-child(4)")
      .get("[data-cy=archive]")
      .eq(0)
      .should("exist");
  });
});
