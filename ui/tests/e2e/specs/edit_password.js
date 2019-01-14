// https://docs.cypress.io/api/introduction/api.html

describe("Testing Editing User Information", () => {
  it(
    "Given: Visits the app root url, logs into an account, navigates" +
      "to the people page, and filters the search to one person",
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
      cy.get("[data-cy=search]").type("Quality");
    }
  );
  it("When: Clicking on the gear button", () => {
    cy.get("[data-cy=admin-person").click();
  });
  it("Then: The person's password can be changed", () => {
    cy.get("[data-cy=new-update-password").type("foobar123");
    cy.get("[data-cy=confirm-password").type("foobar123");
    cy.get("[data-cy=confirm-button]").click();
  });
  it("And: The password can be changed as many times as desired", () => {
    cy.get("[data-cy=admin-person").click();
    cy.get("[data-cy=new-update-password").type("password");
    cy.get("[data-cy=confirm-password").type("password");
    cy.get("[data-cy=confirm-button]").click();
  });
  it("Finally: The new password can be used to log the user in", () => {
    cy.get("[data-cy=cur-locale").click({ multiple: true });
    cy.get("[data-cy=logout]").click();
    cy.get("[data-cy=account-button]").click();
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
    cy.url().should("include", "/admin");
  });
});
