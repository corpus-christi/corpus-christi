//Tests logging into account and then clicking homepage
describe("Clicking home after logging in", function() {
  it("GIVEN: Successful Login", function() {
    cy.login();
    cy.url().should("include", "/admin");
  });
  it("WHEN: Home Button is pressed", function() {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=public]").click();
  });
  it("THEN: Check for Home Page", function() {
    cy.url().should("eq", "http://localhost:8080/");
  });
});

describe("Clicking person and still logged it", function() {
  it("GIVEN: Homepage after login", function() {
    cy.url().should("eq", "http://localhost:8080/");
  });
  it("WHEN: Account bubble is clicked", function() {
    cy.get("[data-cy=account-button]").click();
  });
  it("THEN: Check for Admin Dashboard", function() {
    cy.url().should("include", "/admin");
  });
});
