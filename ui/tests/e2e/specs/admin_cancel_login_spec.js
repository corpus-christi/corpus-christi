describe("Admin Cancel Login Test", function() {
  it("GIVEN: Click on Account bubble", function() {
    cy.visit("/");
    cy.get("[data-cy=account-button]").click();
    cy.url().should("include", "/login");
  });

  it("WHEN: Admin cancels logging in", function() {
    cy.get("[data-cy=cancel]").click();
  });

  it("THEN: Returned to home page", function() {
    cy.url().should("include", "/public");
  });
});
