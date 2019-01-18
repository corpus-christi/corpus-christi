describe("PersonTable Test", function() {
  it("GIVEN: Admin loads PersonTable", function() {
    cy.visit("/login");
    cy.get("[data-cy=username]").type("Cytest");
    //Enters the password
    cy.get("[data-cy=password]").type("password");
    //Clicks the log in button
    cy.get("[data-cy=login]").click();
    cy.url().should("include", "/admin");
    //open nav drawer
    cy.get("[data-cy=toggle-nav-drawer]").click();
    //goes to the people page
    cy.get("[data-cy=people]").click();
  });
  it("WHEN: Admin changes table view", function() {
    cy.get('.v-datatable__actions > :nth-child(1) > :nth-child(1)').click(); //opens up the persons/page dropdown
    cy.get('.v-select-list > .v-list > :nth-child(2)').first().click() //selects the 10 per page option
    //cy.get("[data-cy=person-table]").find(".v-input__control").click();
    //cy.contains("10").click();
  });

  it("THEN: Table shows more rows", function() {
    cy.get("tbody").find("tr")
      .should("have.length", 10);
  });
  it("And: Can navigate to the next/previous page of users", () => {
    cy.get('.v-datatable__actions > :nth-child(2) > :nth-child(3)').click();//advances forward one page
    cy.get('.v-datatable__actions > :nth-child(2) > :nth-child(1)').contains('11-20');//checks to make sure we moved
    cy.get('.v-datatable__actions > :nth-child(2) > :nth-child(2)').click();//Regresses back one page
    cy.get('.v-datatable__actions > :nth-child(2) > :nth-child(1)').contains('1-10');//checks to make sure we moved back

  });
});
