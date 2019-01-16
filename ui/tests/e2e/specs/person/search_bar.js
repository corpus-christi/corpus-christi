// https://docs.cypress.io/api/introduction/api.html

describe("Testing Editing User Information", () => {
  it(
    "Given: Visits the app root url, logs into an account, and navigates " +
      "to the people page",
    () => {
      cy.visit("/");
      //Clicks on the Account button
      cy.get("[data-cy=account-button]").click();
      //Enters the Username
      cy.get("[data-cy=username]").type("Cytest");
      //Enters the password
      cy.get("[data-cy=password]").type("password");
      //Clicks the log in button
      cy.get("[data-cy=login]").click();
      //Making sure we're in the right place
      cy.url().should("include", "/admin");
      //open nav drawer
      cy.get("[data-cy=toggle-nav-drawer]").click();
      //goes to the people page
      cy.get("[data-cy=people]").click();
      // Open the locale menu
      cy.get("[data-cy=cur-locale]").click();
      // Select English locale
      cy.get("[data-cy=en-US]").click();
    }
  );
  it("When: Typing any user-related information into the search bar", () => {
    cy.get("[data-cy=search]").type("Quality");
  });
  it("Then: The table should list entries in which any category contains the searched keyword", () => {
    cy.get("tbody")
      .find("tr")
      .contains("Quality");
  });
  it("And: When searching for something that does not exist, it should let the user know", () => {
    cy.get("[data-cy=search]")
      .clear()
      .type("foobar");
    cy.get("tbody > :nth-child(1) > :nth-child(2)").should("not.exist");
  });
});
