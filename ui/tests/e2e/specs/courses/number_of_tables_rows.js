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

describe("Test for Number of rows", () => {
  it("Testing 5 rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
  });
  it("Testing 10 rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();
  });
  it("Testing 25 rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(3) > .v-list__tile"
    ).click();
  });
  it("Testing All rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(4) > .v-list__tile"
    ).click();
  });
});
