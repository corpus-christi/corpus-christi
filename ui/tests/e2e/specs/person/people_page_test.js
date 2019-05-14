describe("Get to People Page", () => {
  it("GIVEN Successful login", () => {
    cy.login();
  });

  it("WHEN: Clicking to course page", () => {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=people]").click();
  });
  it("THEN: Should be in people page", () => {
    cy.url().should("include", "/people");
  });
});