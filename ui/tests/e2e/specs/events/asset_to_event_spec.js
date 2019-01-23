// NOTE: Requires no assets assigned to events
describe("Add Asset to Event Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to specific event", function() {
    cy.visit("event/1/details");
  });

  it("WHEN: Event planner adds an asset to an event", function() {
    cy.get("[data-cy=add-asset-dialog]").click();
    cy.wait(250);

    cy.get("[data-cy=entity-search-field]")
      .eq(1)
      .click();
    cy.wait(250);
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
    cy.wait(250);
    cy.get("[data-cy=confirm-add]")
      .eq(0)
      .click();
  });

  it("THEN: Asset appears in the list", function() {
    cy.get(
      ":nth-child(3) > [data-v-cee56a84=''] > .ma-1 > .v-list > :nth-child(2) > .v-list__tile > .v-list__tile__content"
    ).should("exist");
  });
});
