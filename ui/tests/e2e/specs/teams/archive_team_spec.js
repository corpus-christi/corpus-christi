describe("Archive Team Test", function() {
  before(() => {
    cy.login();
  });

  it("GIVEN: Event planner goes to teams page", function() {
    cy.visit("/teams/all");
  });

  it("WHEN: Event planner archives a team", function() {
    // Change view to see both archived and active teams
    cy.get(".md3 > .v-input > .v-input__control > .v-input__slot").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile > .v-list__tile__content > .v-list__tile__title"
    ).click();

    cy.get("[data-cy=archive]")
      .eq(0)
      .click();

    cy.get("[data-cy=confirm-archive]").click();
  });

  it("THEN: Team is archived", function() {
    cy.get("[data-cy=unarchive]")
      .eq(0)
      .should("exist");
  });

  it("AND: Team can be unarchived", function() {
    cy.get("[data-cy=unarchive]")
      .eq(0)
      .click();
    cy.get(":nth-child(1) > :nth-child(4)")
      .get("[data-cy=archive]")
      .eq(0)
      .should("exist");
  });
});
