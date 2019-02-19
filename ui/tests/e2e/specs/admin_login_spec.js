describe("Admin Login Test", function() {
  it("GIVEN: Click on Account bubble", function() {
    cy.visit("/");
    cy.get("[data-cy=account-button]").click();
    cy.url().should("include", "/login");
  });

  it("WHEN: Providing correct login credentials", function() {
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
  });

  it("THEN: URL should have /admin", function() {
    cy.url().should("include", "/admin");
  });

  // Not sure if we want to check for content on the base /admin page
  // it('AND: Page content should be Hello, Admin', function() {
  //   cy.get('h1').should('include', 'Hello, Admin');
  // });
});
