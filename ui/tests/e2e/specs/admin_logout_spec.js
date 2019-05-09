describe("Admin Logout Test", function() {
  it("GIVEN: Admin logs in", function() {
    cy.login();
  });

  it("WHEN: Admin logs out", function() {
    cy.url().should("include", "/admin");
    cy.get("[data-cy=account-menu]").click();
    cy.get("[data-cy=logout]").click();
  });

  it("THEN: Returned to home page", function() {
    cy.url().should("eq", "http://localhost:8080/");
  });
});
