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

describe("Edit Diploma Page", () => {
  it("Get to Edit Diploma Page", () => {
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn"
    ).click();
  });
  it("Edit Title", () => {
    cy.get(
      ".v-form > :nth-child(1) > .v-input__control > .v-input__slot > .v-text-field__slot > input"
    ).type("Test Diploma");
  });
  it("Edit Description", () => {
    cy.get("textarea").type("Test description of diploma");
  });
  it("Change Prereqs for diploma", () => {
    cy.get(
      ".v-form > .v-text-field--enclosed > .v-input__control > .v-input__slot > .v-select__slot > .v-select__selections"
    ).click();
    cy.get(
      ".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile > .v-list__tile__content"
    ).click();
  });
  it("Cancel Edit Diploma Page", () => {
    cy.get(
      ".v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .secondary--text"
    ).click();
  });
  it("Save Diploma Page", () => {
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn"
    ).click();
    cy.get(
      ".v-form > :nth-child(1) > .v-input__control > .v-input__slot > .v-text-field__slot > input"
    ).type("Test Diploma");
    cy.get(
      ".v-dialog__content--active > .v-dialog > .v-card > .v-card__actions > .primary"
    ).click();
  });
});
