import { unique_id } from '../../support/helpers';

let new_diploma_title = unique_id();
let new_diploma_title_1 = unique_id();

describe("Edit Diploma Page", () => {
  before(() => {
    cy.login();
    cy.visit("/diplomas");
  });

  it("GIVEN: Edit Diploma Dialog", () => {
    cy.get("[data-cy=edit]").eq(0).click();
  });
  it("WHEN: Editing Diploma", () => {
    cy.get("[data-cy=diplomas-form-name]").clear().type(new_diploma_title);
    cy.get("textarea").clear();
    cy.get("textarea").type(new_diploma_title);
  });

  it("AND: Changing Prereqs", () => {
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click(); // Select a prereq from the drop down

    cy.get(":nth-child(3) > .v-input__icon > .v-icon").click(); // Clear Prereqs
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
    ).click(); // Select an item from the drop down
    cy.get("[data-cy=form-save]").click();
  });

  it("THEN: Find edited diploma", () => {
    cy.get("[data-cy=diplomas-table-search]").type(new_diploma_title); // Search for edited diploma
    cy.get("tbody > tr > :nth-child(1)").click(); // View Diploma details
    cy.get("[data-cy=diploma-name]").contains(new_diploma_title);
    cy.get("[data-cy=diploma-description]").contains(new_diploma_title);
    cy.url().should("include", "/diplomas/");
    cy.get("[data-cy=arrow_back_button]").click();
    cy.url().should("include", "/diplomas");
  });
});

describe("Cancel button functionality test", () => {
  it("GIVEN: Edited diploma", () => {
    cy.get("[data-cy=edit]").eq(0).click();
    cy.get("[data-cy=diplomas-form-name]").clear();
  });

  it("WHEN: User decides to not save changes", () => {
    cy.get("[data-cy=diplomas-form-name]").type(new_diploma_title_1); // This should not save
    cy.get("[data-cy=cancel-new-diploma]").click();
  });

  it("THEN: Make sure it was not saved", () => {
    cy.get("[data-cy=diplomas-table-search]").type(new_diploma_title_1);
    cy.get(".text-xs-center");
  });
});
