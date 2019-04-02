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

let course_name = "New title";

describe("Add Course", () => {
  it("Given: New Course Form", () => {
    cy.get("[data-cy=courses-table-new]").click();
  });
  it("When: Form is filled out", () => {
    cy.get("[data-cy=course-form-name]").type(course_name);
    cy.get("[data-cy=course-form-description]").type("This should work!");
  });
  it("Then: Click add button", () => {
    cy.get("[data-cy=course-editor-actions] > .primary").click();
  });
});

describe("Archive Courses", () => {
  it("click archive button", () => {
    cy.get("[data-cy=courses-table-search]").type(course_name);
    //cy.contains('Debate until.').click()
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(2) > span > .v-btn"
    ).click(); //click archive
    cy.get(
      ".v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary"
    ).click(); //confirm click
  });
  it("check archive course", () => {
    cy.get(".v-text-field--solo > .v-input__control > .v-input__slot").click(); //switch from active to archive
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click(); //select archive in drop down
    cy.get("tbody").contains(course_name);
  });
});

describe("Activate archive courses", () => {
  it("click activate button", () => {
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(2) > span > .v-btn"
    ).click();
  });
  it("Get back to active courses", () => {
    cy.get(".v-text-field--solo > .v-input__control > .v-input__slot").click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
    cy.get("tbody > tr > :nth-child(1)").contains(course_name);
  });
});
