describe("Login Test", function() {
  it("tests whether login function is working with user Cytest", () => {
    cy.visit("/");
    cy.get("[data-cy=account-button]").click();
    cy.url().should("include", "/login");
  });

  it("WHEN: Providing correct login credentials", function() {
    cy.get("[data-cy=username]").type("Cytest");
    cy.get("[data-cy=password]").type("password");
    cy.get("[data-cy=login]").click();
  });

  it("THEN: We should land on the people page", function() {
    cy.url().should("include", "/people");
  });
});
