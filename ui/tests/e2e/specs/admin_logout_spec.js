describe("Admin Logout Test", function() {
  it("GIVEN: Admin logs in", function() {
    cy.visit("/login");
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
  });

  it("WHEN: Admin logs out", function() {
    cy.url().should("include", "/admin");
    cy.get("[data-cy=account-menu]").click();
    cy.get("[data-cy=logout]").click();
  });

  it("THEN: Returned to home page", function() {
    cy.url().should("include", "/public");
  });
});
