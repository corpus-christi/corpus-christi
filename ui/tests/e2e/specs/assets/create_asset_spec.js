describe("Create Asset Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to Assets page", function() {
    cy.visit("/assets");
  });

  it("WHEN: Event planner creates a new asset", function() {
    cy.get("[data-cy=add-asset]").click();

    cy.get("[data-cy=description]").type("A whole new Asset");

    // Get the first location in the list
    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();

    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: A new asset is listed", function() {
    cy.get("tbody").contains("A whole new Asset");
  });
});
