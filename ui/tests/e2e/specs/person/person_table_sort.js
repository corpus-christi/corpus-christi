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
    }
  );
  it("When: clicking on a sorting method: last name descending", () => {
    cy.get("thead > :nth-child(1) > :nth-child(3)").click();
  });
  it("Then: The table should resort itself based on what was being sorted", () => {
    cy.get("tbody > :nth-child(1) > :nth-child(3)").contains("Alcaraz");
  });

  it("And: When clicked again should change the sorting method: last name ascending", () => {
    cy.get("thead > :nth-child(1) > :nth-child(3)").click();
    cy.get("tbody > :nth-child(1) > :nth-child(3)").contains("Ziffle");
  });
  it("And: When clicked again should change the sorting method: last name by user_id", () => {
    cy.get("thead > :nth-child(1) > :nth-child(3)").click();
    cy.get("tbody > :nth-child(1) > :nth-child(3)").contains("Higgins");
  });
  it("And: The other sorting buttons should be clickable and work as well", () => {
    cy.get("thead > :nth-child(1) > :nth-child(2)").click();
    cy.get("tbody > :nth-child(1) > :nth-child(2)").contains("Adalberto");
    cy.get("thead > :nth-child(1) > :nth-child(4)").click().click();
    cy.get("tbody > :nth-child(1) > :nth-child(4)").contains("usalcedo@gmail.com");
    cy.get("thead > :nth-child(1) > :nth-child(5)").click();
    cy.get("tbody > :nth-child(1) > :nth-child(5)").should("be.empty");
  });
});
