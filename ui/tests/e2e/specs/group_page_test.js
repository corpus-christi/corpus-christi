//Tests logging in and going to the group page
describe("Clicking home after logging in", function() {
  it("Given: logs in successfully", function() {
    cy.visit("/login");
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
    cy.url().should("include", "/admin");
  });
  it("When: group tab is pressed", function() {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=groups]").click();
  });
  it("Then: url should have /groups", function() {
    cy.url().should("include", "/groups");
  });
});
