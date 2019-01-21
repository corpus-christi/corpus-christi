// NOTE: Requires no team members assigned to event
describe("Add Team Member Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to a specific team", function() {
    cy.visit("/teams/1");
  });

  it("WHEN: Event planner adds a new person to the team", function() {
    cy.get("[data-cy=add-team-member]").click();

    cy.wait(250);

    cy.get("[data-cy=entity-search-field]").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();

    cy.get("[data-cy=confirm-participant]").click();
  });

  it("THEN: A new team member is listed", function() {
    cy.get("tbody > :nth-child(1)").should("exist");
  });

  it("AND: The team member can be archived and unarchived", function() {
    cy.get("[data-cy=archive]")
      .eq(0)
      .click();
    cy.get("[data-cy=confirm-archive]").click();

    cy.get("[data-cy=unarchive]").should("exist");

    cy.get("[data-cy=unarchive]")
      .eq(0)
      .click();

    cy.get("[data-cy=archive]").should("exist");
  });

  // TODO: Add a new person entirely, not just an existing person
});
