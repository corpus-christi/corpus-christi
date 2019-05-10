import { unique_id } from '../../support/helpers';

let diploma_title = unique_id();

describe("Fill out new diploma form and cancel", () => {
  before(() => {
    cy.login();
    cy.visit("/diplomas");
  });
  it("GIVEN: New Diploma Form", () => {
    cy.get("[data-cy=diplomas-table-new]").click();
  });

  it("WHEN: Filling out new diploma form", () => {
    cy.get("[data-cy=diplomas-form-name]").type(diploma_title); // Title
    cy.get("[data-cy=diploma-form-description]").type("Epic Dance Party"); // Description
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile").click(); // Select an item from the drop down
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile").click(); // Select another item from the drop down
  });

  it("THEN: Test cancel diploma", () => {
    cy.get("[data-cy=cancel-new-diploma]").click();
  });
});

describe("Fill-out incomplete diploma", () => {
  it("GIVEN: New Diploma Form", () => {
    cy.get("[data-cy=diplomas-table-new]").click();
  });

  it("WHEN: Form is filled-out with missing title & sescription", () => {
    // cy.get("[data-cy=diplomas-form-name]").type(diploma_title); // Title
    // cy.get("[data-cy=diploma-form-description]").type("Epic Dance Party"); // Description
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
      ).click(); // Select an item from the drop down
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
      ).click(); // Select another item from the drop down
  });

  it("THEN: Try to save an incomplete form", () => {
    cy.get("[data-cy=form-save]").click(); // Click save button
    cy.get(".v-messages__message"); // Check to get error message
    cy.get(".v-textarea > .v-input__control > .v-text-field__details > .v-messages > .v-messages__wrapper > .v-messages__message"); // Check to get error message
  });
});

describe("Add diploma", () => {
  it("GIVEN: Finish Filling-out New Diploma Form", () => {
    cy.get("[data-cy=diplomas-form-name]").type(diploma_title); // Title
    cy.get("[data-cy=diploma-form-description]").type("Epic Dance Party"); // Description
  });

  it("WHEN: Saving diploma", () => {
    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: Checking the added diploma", () => {
    cy.get("[data-cy=diplomas-table-search]").type(diploma_title);
    cy.get("tbody > :nth-child(1) ").click();
    cy.url().should("include", "/diplomas/");
  });
});
