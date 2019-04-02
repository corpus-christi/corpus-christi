let course = "Alone low investment";

describe("Get to details of a course page", () => {
  it("Given: Successfull login", () => {
    cy.login();
  });
  it("When: clicking to course page", () => {
    cy.course_page();
  });
  it("Then: should be in course page", () => {
    cy.url().should("include", "/courses");
  });
  it("Click into details of course", () => {
    cy.get("tbody")
      .contains(course)
      .click();
    cy.url().should("include", "/courses/1");
  });
});

describe("Edit course section", () => {
  it("edit existing course section", () => {
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn"
    ).click();
  });
  it("Edit description", () => {
    cy.get("[data-cy=course-offering-description]").type("Hello world part 3");
  });
  // it("Edit date", () => {
  //   cy.get(
  //     ".v-menu__activator > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-select__selections > input"
  //   ).click();
  //   cy.get(":nth-child(5) > :nth-child(2) > .v-btn").click();
  //   cy.get(".v-picker__actions > :nth-child(2)").click(); //cancel button
  //   cy.get(
  //     ".v-menu__activator > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-select__selections > input"
  //   ).click();
  //   cy.get(":nth-child(5) > :nth-child(2) > .v-btn").click();
  //   cy.get(".v-picker__actions > :nth-child(3)").click(); //save button
  // });
});
