describe("Get to Diplomas Page", () => {
  it("Given Successfull login", () => {
    cy.login();
  });
  it("When: clicking to diplomas page", () => {
    cy.deploma_page();
  });
  it("Then: should be in diplomas page", () => {
    cy.url().should("include", "/diplomas");
  });
});

describe("Fill out New Diploma Form", () => {
  it("New Diploma Button", () => {
    cy.get("[data-cy=diplomas-table-new]").click();
  });
  it("Fill out new diploma form", () => {
    cy.get(
      ".v-form > :nth-child(1) > .v-input__control > .v-input__slot > .v-text-field__slot > input"
    ).type("Its Friday!!!");
    cy.get("textarea").type("Epic Dance Party");
    cy.get(
      ".v-form > .v-text-field--enclosed > .v-input__control > .v-input__slot > .v-select__slot"
    ).click(); //lists of prereqs
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click(); //alone low investment
    cy.get(
      ".v-form > .v-text-field--enclosed > .v-input__control > .v-input__slot > .v-select__slot > .v-select__selections"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();
  });
  it("Cancel new diploma", () => {
    cy.get(
      ".v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .secondary--text"
    ).click();
  });
});

describe("Fill out New Diploma Form half way", () => {
  it("New Diploma Button", () => {
    cy.get("[data-cy=diplomas-table-new]").click();
  });
  it("Fill out new diploma form", () => {
    cy.get(
      ".v-form > :nth-child(1) > .v-input__control > .v-input__slot > .v-text-field__slot > input"
    ).type("Half way gone!!");
    cy.get(
      ".v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary"
    ).click();
  });
});

let new_diploma = "Its Friday!!!";

describe("Add Diploma", () => {
  it("Filling out new diploma form", () => {
    cy.get("[data-cy=diplomas-table-new]").click();
    cy.get(
      ".v-form > :nth-child(1) > .v-input__control > .v-input__slot > .v-text-field__slot > input"
    ).type(new_diploma);
    cy.get("textarea").type("Epic Dance Party");
    cy.get(
      ".v-form > .v-text-field--enclosed > .v-input__control > .v-input__slot > .v-select__slot"
    ).click(); //lists of prereqs
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click(); //alone low investment
    cy.get(
      ".v-form > .v-text-field--enclosed > .v-input__control > .v-input__slot > .v-select__slot > .v-select__selections"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(2) > .v-list__tile"
    ).click();
    cy.get(
      ".v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary"
    ).click();
  });
  it("checking the added diploma", () => {
    cy.get("[data-cy=diplomas-table-search]").type(new_diploma);
    cy.get("tbody > :nth-child(1) ").click();
    cy.url().should("include", "/diplomas/33");
  });
});
