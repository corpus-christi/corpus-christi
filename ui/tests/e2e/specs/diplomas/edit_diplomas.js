import { unique_id } from '../../support/helpers';

let new_diploma_title = unique_id();
let new_diploma_title_1 = unique_id();

describe("Get to Diplomas Page", () => {
  it("GIVEN: Successful login", () => {
    cy.login();
  });
  it("WHEN: clicking to diplomas page", () => {
    cy.deploma_page();
  });
  it("THEN: should be in diplomas page", () => {
    cy.url().should("include", "/diplomas");
  });
});

describe("Edit Diploma Page", () => {
  it("GIVEN:  Edit Diploma Page", () => {
    cy.get(
      ":nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn > .v-btn__content > .v-icon"
    ).click();
  });

  it("Edit Title", () => {
    cy.get("[data-cy=diplomas-form-name]").clear();
    cy.get("[data-cy=diplomas-form-name]").type(new_diploma_title + " Test Diploma");
  });

  it("Edit Description", () => {
    cy.get("textarea").clear();
    cy.get("textarea").type(new_diploma_title);
  });

  it("Change Prereqs for diploma", () => {
    cy.get(":nth-child(3) > .v-input__icon > .v-icon").click(); // Clear Prereqs
    cy.get(":nth-child(4) > .v-input__icon > .v-icon").click(); // Click drop down
    cy.get(".menuable__content__active > .v-select-list > .v-list > :nth-child(1) > .v-list__tile"
      ).click(); // Select an item from the drop down
    cy.get("[data-cy=form-save]").click(); // Click save button
  });

  it("Find edited diploma", () => {
    cy.get("[data-cy=diplomas-table-search]").type(new_diploma_title + " Test Diploma"); // Search for edited diploma
    cy.get("tbody > tr > :nth-child(1)").click(); // View Diploma details
    cy.get("[data-cy=diploma-name]").contains(new_diploma_title + " Test Diploma");
    cy.get("[data-cy=diploma-description]").contains(new_diploma_title);
    cy.url().should("include", "/diplomas/");
    cy.get("[data-cy=arrow_back_button]").click();
    cy.url().should("include", "/diplomas");
  })
});

describe("Cancel button functionality test", () => {
  it("GIVEN: Edited diploma", () => {
    cy.get(":nth-child(1) > :nth-child(3) > .layout > :nth-child(1) > span > .v-btn").click();
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
