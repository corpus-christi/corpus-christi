// NOTE: Requires no teams assigned to any events
describe("Event Teams Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to event details", function() {
    cy.visit("/event/1/details");
  });

  it("WHEN: Event planner adds a team to an event", function() {
    cy.get("[data-cy=add-team-dialog]").click();

    cy.wait(250);

    cy.get("[data-cy=entity-search-field]")
      .eq(3)
      .click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();

    cy.get("[data-cy=confirm-add]")
      .eq(2)
      .click();
  });

  it("THEN: A new team is listed for the event", function() {
    cy.get(".ma-1 > .v-list > :nth-child(2)").should("exist");
  });

  it("AND: Event planner adds another team", function() {
    cy.get("[data-cy=add-team-dialog]").click();

    cy.wait(250);

    cy.get("[data-cy=entity-search-field]")
      .eq(0)
      .click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();

    cy.get("[data-cy=confirm-add]").click();
  });

  it("THEN: Event has multiple teams", function() {
    cy.get(".ma-1 > .v-list > :nth-child(4)").should("exist");
  });

  it("AND: Event planner can remove a team", function() {
    cy.get("[data-cy=deleteTeam-1]").click();
    cy.get("[data-cy=confirm-delete]").click();

    cy.get(".ma-1 > .v-list > :nth-child(4)").should("not.exist");
  });
});
