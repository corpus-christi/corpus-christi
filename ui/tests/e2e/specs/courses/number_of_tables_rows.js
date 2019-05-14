describe("Test for Number of rows", () => {
  before(() => {
    cy.login();
    cy.visit("/courses");
  });
  it("Testing 10 rows", () => {
    cy.get(
      ".v-datatable__actions__select > .v-input > .v-input__control > .v-input__slot > .v-select__slot > .v-input__append-inner > .v-input__icon > .v-icon"
    ).click();
    cy.get(
      ".v-menu__content--auto > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click();
    cy.get("tbody :nth-child(9)");
  });
  it("Testing 15 rows", () => {
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
