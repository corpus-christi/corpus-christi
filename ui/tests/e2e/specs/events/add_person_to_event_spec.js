// NOTE: Requires that no people are tied to other events
describe("Event Person Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to an event's details", function() {
    cy.visit("/event/1/details");
  });

  it("WHEN: Event planner adds a new person", function() {
    cy.get("[data-cy=add-person-dialog]").click();
    cy.get("[data-cy=person-entity-search]").click();

    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
    cy.get("[data-cy=description]")
      .eq(1)
      .type("Cool description of a dude.");

    cy.get("[data-cy=confirm-add]")
      .eq(1)
      .click();
  });

  it("THEN: A new person is added to the event", function() {
    cy.get(
      ".column > :nth-child(2) > [data-v-cee56a84=''] > .ma-1 > .v-list > :nth-child(2) > .v-list__tile"
    ).should("exist");
  });

  it("AND: Person can be removed from event", function() {
    cy.get(
      ".column > :nth-child(2) > [data-v-cee56a84=''] > .ma-1 > .v-list > :nth-child(2) > .v-list__tile > .v-list__tile__action > :nth-child(1) > :nth-child(2)"
    ).click();
    cy.get(
      ".column > :nth-child(2) > [data-v-cee56a84=''] > .ma-1 > .v-list > :nth-child(2) > .v-list__tile"
    ).should("not.exist");
  });
});
