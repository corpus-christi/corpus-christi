describe("Get to Courses Page", () => {
  it("Given Successfull login", () => {
    cy.visit("/");
    cy.get("[data-cy=account-button]").click();
    cy.get("[data-cy=username]").type("lpratico");
    cy.get("[data-cy=password]").type("Qwerty1234");
    cy.get("[data-cy=login]").click();
  });

  it("When: clicking to course page", () => {
    cy.get("[data-cy=open-navigation]").click();
    cy.get(":nth-child(5) > .v-list__tile").click();
  });
  it("Then: should be in course page", () => {
    cy.url().should("include", "/courses");
  });
});

describe("Add Course", () => {
  it("Given: New Course Form", () => {
    cy.get("[data-cy=courses-table-new]").click();
  });
  it("When: Form is filled out", () => {
    cy.get("[data-cy=course-form-name]").type("COS 5");
    cy.get("[data-cy=course-form-description]").type("Hello World");
  });
  it("Then: Click add button", () => {
    cy.get("[data-cy=course-editor-actions] > .primary").click();
    cy.get(
      ":nth-child(5) > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(3) > .v-list__tile"
    ).click;
  });
});
