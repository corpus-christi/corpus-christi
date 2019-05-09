describe("Admin Login Test", function() {
  it("GIVEN: Click on Account bubble", function() {
    cy.visit("/");
    cy.get("[data-cy=account-button]").click();
    cy.url().should("include", "/login");
  });

  it("WHEN: Providing correct login credentials", function() {
    cy.login();
  });

  it("THEN: URL should have /admin", function() {
    cy.url().should("include", "/admin");
  });
});
