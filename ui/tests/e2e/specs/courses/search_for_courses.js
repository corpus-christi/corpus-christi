describe("Get to Courses Page", () => {
  it("Given Successfull login", () => {
    cy.login();
  });

  it("When: clicking to course page", () => {
    cy.get("[data-cy=toggle-nav-drawer]").click();
    cy.get("[data-cy=courses]").click();
  });
  it("Then: should be in course page", () => {
    cy.url().should("include", "/courses");
  });
});

describe("search for courses that exist", () => {
  it("When: course name is typed", () => {
    cy.get("[data-cy=courses-table-search]").type("Alone");
  });
  it("Then: should find course name", () => {
    cy.get("tbody > :nth-child(1) > :nth-child(1)").contains("Alone");
  });
});

describe("search for courses that does not exist", () => {
  it("When: course name is typed", () => {
    cy.get("[data-cy=courses-table-search]")
      .clear()
      .type("Not Here");
  });
  it("Then: should find nothing", () => {
    cy.get("tbody > :nth-child(1) > :nth-child(1)").contains(
      "No se encontraron registros coincidentes"
    );
  });
});
