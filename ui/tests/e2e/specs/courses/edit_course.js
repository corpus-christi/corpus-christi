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

describe("Edit courses", () => {
  it("Open edit course", () => {
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn"
    ).click();
  });
  it("change course title", () => {
    cy.get("[data-cy=course-form-name]")
      .clear()
      .type("Alone low investment");
  });
  it("save changes", () => {
    cy.get("[data-cy=course-editor-actions] > .primary").click();
  });
});
