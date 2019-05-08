describe("Get to Courses Page", () => {
  it("GIVEN Successful login", () => {
    cy.login();
  });

  it("WHEN: Clicking to course page", () => {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=courses]").click();
  });
  it("THEN: Should be in course page", () => {
    cy.url().should("include", "/courses");
  });
});