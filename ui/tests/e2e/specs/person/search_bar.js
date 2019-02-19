// https://docs.cypress.io/api/introduction/api.html

describe("Testing Editing User Information", () => {
  it(
    "Given: Visits the app root url, logs into an account, and navigates " +
      "to the people page",
    () => {
      cy.login();
      //Making sure we're in the right place
      cy.url().should("include", "/admin");
      //open nav drawer
      cy.get("[data-cy=toggle-nav-drawer]").click();
      //goes to the people page
      cy.get("[data-cy=people]").click();
    }
  );
  it("When: Typing any user-related information into the search bar", () => {
    cy.get("[data-cy=search]").type("Quality");
  });
  it("Then: The table should list entries in which any category contains the searched keyword", () => {
    cy.get("[data-cy=person-table").within(() => {
      cy.get("tbody > :nth-child(1) > :nth-child(2)").should(
        "contain",
        "Quality"
      );
      cy.get("tbody > :nth-child(1) > :nth-child(3)").should(
        "contain",
        "Assurance"
      );
    });
  });
  it("And: When searching for something that does not exist, it should let the user know", () => {
    cy.get("[data-cy=search]")
      .clear()
      .type("foobar");
    cy.get("[data-cy=person-table").within(() => {
      cy.get("tbody > :nth-child(1) > :nth-child(2)").should("not.exist");
    });
  });
});
