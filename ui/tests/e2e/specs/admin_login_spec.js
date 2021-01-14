describe("Admin Login Test", function () {
  it("GIVEN: Click on Account bubble", function () {
    cy.visit("/");
    cy.get("[data-cy=account-button]").click();
    cy.url().should("include", "/login");
  });
  it("WHEN: Clicks the language button", () => {
    cy.get("[data-cy=cur-locale]").click();
  });
  it("WHEN: Switches the language", () => {
    cy.get("[data-cy=language-dropdown]").click("center");
  });
  it("WHEN: Providing correct login credentials", function () {
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
  });
  it("THEN: Switch to Group Page", function () {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=groups]").click();
    cy.location("pathname").should("include", "/groups/all");
  });
  it("THEN: Check for permission ", function () {
    cy.wait(1000).get('*[class^="shrink col"]').eq(1).click();
    cy.get('*[class^="v-list-item__content"]').contains(" Manage Group Types ");
  });
  //Current solution for checking if the logged in user is admin or not by reading content from the Home-Group module
});
