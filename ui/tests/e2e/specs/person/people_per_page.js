describe("PersonTable Test", function() {
  it("GIVEN: Admin loads PersonTable", function() {
    cy.login();
    cy.url().should("include", "/admin");
    //open nav drawer
    cy.get("[data-cy=toggle-nav-drawer]").click();
    //goes to the people page
    cy.get("[data-cy=people]").click();
  });
  it("WHEN: Admin changes table view", function() {
    cy.get("[data-cy=person-table]").within(() => {
      cy.get(".v-datatable__actions > :nth-child(1) > :nth-child(1)").click(); //opens up the persons/page dropdown
    });
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile > .v-list__tile__content > .v-list__tile__title"
    )
      .first()
      .click(); //selects the 10 per page option
    //cy.get("[data-cy=person-table]").find(".v-input__control").click();
    //cy.contains("10").click();
  });

  it("THEN: Table shows more rows", function() {
    cy.get("[data-cy=person-table]").within(() => {
      cy.get("tbody")
        .find("tr")
        .should("have.length", 10);
    });
  });
  it("And: Can navigate to the next/previous page of users", () => {
    cy.get("[data-cy=person-table]").within(() => {
      cy.get(".v-datatable__actions > :nth-child(2) > :nth-child(3)").click(); //advances forward one page
      cy.get(".v-datatable__actions > :nth-child(2) > :nth-child(1)").contains(
        "11-20"
      ); //checks to make sure we moved
      cy.get(".v-datatable__actions > :nth-child(2) > :nth-child(2)").click(); //Regresses back one page
      cy.get(".v-datatable__actions > :nth-child(2) > :nth-child(1)").contains(
        "1-10"
      ); //checks to make sure we moved back
    });
  });
});
