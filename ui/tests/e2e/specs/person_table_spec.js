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
    cy.get('[data-cy=open-navigation]')
      .click();
    //goes to the people page
    cy.get("[data-cy=people]").click();
  });
  it("WHEN: Admin changes table view", function() {
    cy.get("[data-cy=person-table]")
      .find(".v-input__control")
      .click();
    // TODO: Ugly way to change the number of rows, alternative???
    cy.contains("10").click();
  });

  it("THEN: Table shows more rows", function() {
    cy.get("tbody")
      .find("tr")
      .should("have.length", 10);
  });

  // TODO: Test switching through pages of the table
  // it('AND: Table shows next page', function() {
  //   cy.get('[data-cy=person-table]').find('.v-icon material-icons theme--light').click();
  // });
});
