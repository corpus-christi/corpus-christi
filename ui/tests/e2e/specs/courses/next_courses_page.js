describe("Get to Courses Page", () => {
  it("GIVEN Successful login", () => {
    cy.login();
  });

  it("WHEN: clicking to course page", () => {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=courses]").click();
  });
  it("THEN: should be in course page", () => {
    cy.url().should("include", "/courses");
  });
});

describe("Flip through Courses Page", () => {
  it("Next page", () => {
    cy.get('[aria-label="Siguiente página"]').click();
  });
  it("back page", () => {
    cy.get('[aria-label="Pagina anterior"]').click();
  });
});
