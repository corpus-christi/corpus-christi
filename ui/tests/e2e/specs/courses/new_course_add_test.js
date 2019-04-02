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

describe("Add Course", () => {
  it("Given: New Course Form", () => {
    cy.get("[data-cy=courses-table-new]").click();
  });
  it("When: Form is filled out", () => {
    cy.get("[data-cy=course-form-name]").type("COS 123");
    cy.get("[data-cy=course-form-description]").type("Hello World");
  });
  it("Then: Click add button", () => {
    cy.get("[data-cy=course-editor-actions] > .primary").click();
    cy.get("[data-cy=courses-table-search]").type("COS 123");
  });
});

describe("Attempt to Add Course Without Title", () => {
  it("Given: New Course Form", () => {
    cy.get("[data-cy=courses-table-new]").click();
  });
  it("When: Just Title is filled out", () => {
    cy.get("[data-cy=course-form-name]").type("COS 6");
  });
  it("Then: Click Add Button", () => {
    cy.get("[data-cy=course-editor-actions] > .primary").click();
  });
  it("Adding Course should fail", () => {
    cy.wait(500);
    cy.contains("Se fall");
  });
});

describe("Add Course with a Prereq", () => {
  it("Given: New Course Form", () => {
    cy.get("[data-cy=courses-table-new]").click();
  });
  it("When: Form is filled out", () => {
    cy.get("[data-cy=course-form-name]").type("COS 113");
    cy.get("[data-cy=course-form-description]").type("Hello World");
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(4) > .v-list__tile > .v-list__tile__content"
    ).click();
  });
  it("Then: Click add button", () => {
    cy.get("[data-cy=course-editor-actions] > .primary").click();
    cy.get("[data-cy=courses-table-search]")
      .clear()
      .type("COS 113");
  });
});

describe("Add Course with Muiltiple Prereq", () => {
  it("Given: New Course Form", () => {
    cy.get("[data-cy=courses-table-new]").click();
  });
  it("When: Form is filled out", () => {
    cy.get("[data-cy=course-form-name]").type("COS 115");
    cy.get("[data-cy=course-form-description]").type("Hello World");
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile > .v-list__tile__content"
    ).click();
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile > .v-list__tile__content"
    ).click();
  });
  it("Then: Click add button", () => {
    cy.get("[data-cy=course-editor-actions] > .primary").click();
    cy.get("[data-cy=courses-table-search]")
      .clear()
      .type("COS 115");
    //cy.get(':nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn').click()
  });
});
